import logging
import sqlite3
import uuid

from flask import jsonify, render_template, request

from helpdesk.db import get_db, utc_now
from helpdesk.validation import (
    STATUSES,
    ValidationError,
    parse_uuid,
    required_text,
    validate_ticket_payload,
)

logger = logging.getLogger(__name__)
FILTER_VALUES = {
    "category": frozenset({"Hardware", "Software", "Network", "Other"}),
    "priority": frozenset({"Low", "Medium", "High"}),
    "status": STATUSES,
}


def _error(message, status, code="validation_error", field=None):
    details = {"code": code, "message": message}
    if field:
        details["field"] = field
    return jsonify({"error": details}), status


def _json_body():
    if not request.is_json:
        raise ValidationError("Content-Type must be application/json.")
    payload = request.get_json(silent=True)
    if payload is None:
        raise ValidationError("Request body must contain valid JSON.")
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")
    return payload


def _ticket_row(ticket_id):
    return get_db().execute(
        """
        SELECT tickets.*, technicians.name AS technician_name
        FROM tickets
        LEFT JOIN technicians ON technicians.id = tickets.technician_id
        WHERE tickets.id = ?
        """,
        (ticket_id,),
    ).fetchone()


def _serialize_ticket(row):
    ticket = dict(row)
    ticket["assigned_technician"] = ticket.pop("technician_name")
    return ticket


def register_routes(app):
    @app.errorhandler(sqlite3.Error)
    def handle_database_error(error):
        logger.exception("Help desk database operation failed")
        return _error("The database operation failed. No changes were saved.", 500, "database_error")

    @app.get("/healthz")
    def health_check():
        get_db().execute("SELECT 1").fetchone()
        return jsonify({"status": "ok"})

    @app.get("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.get("/tickets/new")
    def new_ticket_page():
        return render_template("new_ticket.html")

    @app.get("/tickets/<ticket_id>")
    def ticket_details_page(ticket_id):
        return render_template("ticket_details.html", ticket_id=ticket_id)

    @app.get("/api/technicians")
    def list_technicians():
        rows = get_db().execute(
            "SELECT id, name FROM technicians ORDER BY name COLLATE NOCASE"
        ).fetchall()
        return jsonify({"technicians": [dict(row) for row in rows]})

    @app.get("/api/tickets")
    def list_tickets():
        clauses = []
        parameters = []
        room = request.args.get("room", "").strip()
        if room:
            clauses.append("instr(lower(tickets.room), lower(?)) > 0")
            parameters.append(room)
        for field, allowed_values in FILTER_VALUES.items():
            value = request.args.get(field)
            if value is not None and value != "":
                if value not in allowed_values:
                    return _error(f"Unsupported {field}.", 400, field=field)
                clauses.append(f"tickets.{field} = ?")
                parameters.append(value)
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = get_db().execute(
            f"""
            SELECT tickets.*, technicians.name AS technician_name
            FROM tickets
            LEFT JOIN technicians ON technicians.id = tickets.technician_id
            {where_clause}
            ORDER BY tickets.created_at DESC, tickets.id
            """,
            parameters,
        ).fetchall()
        return jsonify({"tickets": [_serialize_ticket(row) for row in rows]})

    @app.post("/api/tickets")
    def create_ticket():
        try:
            ticket = validate_ticket_payload(_json_body())
        except ValidationError as error:
            return _error(str(error), 400, field=error.field)

        ticket_id = str(uuid.uuid4())
        created_at = utc_now()
        connection = get_db()
        with connection:
            connection.execute(
                """
                INSERT INTO tickets
                    (id, room, device, category, description, priority, status,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 'Open', ?, ?)
                """,
                (
                    ticket_id,
                    ticket["room"],
                    ticket["device"],
                    ticket["category"],
                    ticket["description"],
                    ticket["priority"],
                    created_at,
                    created_at,
                ),
            )
        return jsonify({"ticket": _serialize_ticket(_ticket_row(ticket_id))}), 201

    @app.get("/api/tickets/<ticket_id>")
    def get_ticket(ticket_id):
        if parse_uuid(ticket_id) is None:
            return _error("Ticket ID must be a valid UUID.", 400, field="ticket_id")
        row = _ticket_row(ticket_id.lower())
        if row is None:
            return _error("Ticket was not found.", 404, "not_found")
        return jsonify({"ticket": _serialize_ticket(row)})

    @app.get("/api/tickets/<ticket_id>/history")
    def get_ticket_history(ticket_id):
        if parse_uuid(ticket_id) is None:
            return _error("Ticket ID must be a valid UUID.", 400, field="ticket_id")
        connection = get_db()
        if connection.execute(
            "SELECT 1 FROM tickets WHERE id = ?", (ticket_id.lower(),)
        ).fetchone() is None:
            return _error("Ticket was not found.", 404, "not_found")
        rows = connection.execute(
            """
            SELECT old_status, new_status, changed_at
            FROM ticket_status_history
            WHERE ticket_id = ?
            ORDER BY id
            """,
            (ticket_id.lower(),),
        ).fetchall()
        return jsonify({"history": [dict(row) for row in rows]})

    @app.patch("/api/tickets/<ticket_id>/assignment")
    def update_assignment(ticket_id):
        if parse_uuid(ticket_id) is None:
            return _error("Ticket ID must be a valid UUID.", 400, field="ticket_id")
        try:
            payload = _json_body()
        except ValidationError as error:
            return _error(str(error), 400, field=error.field)
        if "technician_id" not in payload:
            return _error("Technician ID is required; use null to clear assignment.", 400, field="technician_id")
        technician_id = payload["technician_id"]
        if technician_id is not None and (
            not isinstance(technician_id, str) or not technician_id.strip()
        ):
            return _error("Choose a listed technician or null.", 400, field="technician_id")
        if technician_id is not None:
            technician_id = technician_id.strip()
            exists = get_db().execute(
                "SELECT 1 FROM technicians WHERE id = ?", (technician_id,)
            ).fetchone()
            if exists is None:
                return _error("Technician was not found.", 400, field="technician_id")

        connection = get_db()
        with connection:
            cursor = connection.execute(
                "UPDATE tickets SET technician_id = ?, updated_at = ? WHERE id = ?",
                (technician_id, utc_now(), ticket_id.lower()),
            )
            if cursor.rowcount == 0:
                return _error("Ticket was not found.", 404, "not_found")
        return jsonify({"ticket": _serialize_ticket(_ticket_row(ticket_id.lower()))})

    @app.patch("/api/tickets/<ticket_id>/status")
    def update_status(ticket_id):
        if parse_uuid(ticket_id) is None:
            return _error("Ticket ID must be a valid UUID.", 400, field="ticket_id")
        try:
            payload = _json_body()
        except ValidationError as error:
            return _error(str(error), 400, field=error.field)

        target_status = payload.get("status")
        if not isinstance(target_status, str) or target_status not in STATUSES:
            return _error("Choose a supported status.", 400, field="status")
        resolution_notes = None
        if target_status == "Resolved":
            try:
                resolution_notes = required_text(payload, "resolution_notes")
            except ValidationError as error:
                return _error(str(error), 400, field=error.field)

        connection = get_db()
        with connection:
            current = connection.execute(
                "SELECT status FROM tickets WHERE id = ?", (ticket_id.lower(),)
            ).fetchone()
            if current is None:
                return _error("Ticket was not found.", 404, "not_found")
            old_status = current["status"]
            if (old_status, target_status) not in {
                ("Open", "In Progress"),
                ("In Progress", "Resolved"),
            }:
                return _error(
                    f"Transition from {old_status} to {target_status} is not allowed.",
                    400,
                    field="status",
                )

            changed_at = utc_now()
            if target_status == "Resolved":
                cursor = connection.execute(
                    """
                    UPDATE tickets
                    SET status = ?, resolution_notes = ?, resolved_at = ?, updated_at = ?
                    WHERE id = ? AND status = ?
                    """,
                    (
                        target_status,
                        resolution_notes,
                        changed_at,
                        changed_at,
                        ticket_id.lower(),
                        old_status,
                    ),
                )
            else:
                cursor = connection.execute(
                    """
                    UPDATE tickets SET status = ?, updated_at = ?
                    WHERE id = ? AND status = ?
                    """,
                    (target_status, changed_at, ticket_id.lower(), old_status),
                )
            if cursor.rowcount != 1:
                raise sqlite3.IntegrityError("Ticket status changed concurrently.")
            connection.execute(
                """
                INSERT INTO ticket_status_history (ticket_id, old_status, new_status, changed_at)
                VALUES (?, ?, ?, ?)
                """,
                (ticket_id.lower(), old_status, target_status, changed_at),
            )
        return jsonify({"ticket": _serialize_ticket(_ticket_row(ticket_id.lower()))})

    @app.errorhandler(404)
    def handle_not_found(error):
        if request.path.startswith("/api/"):
            return _error("API endpoint was not found.", 404, "not_found")
        return "Page not found.", 404

    @app.errorhandler(500)
    def handle_internal_error(error):
        if request.path.startswith("/api/"):
            return _error("An unexpected server error occurred.", 500, "server_error")
        return "An unexpected server error occurred.", 500
