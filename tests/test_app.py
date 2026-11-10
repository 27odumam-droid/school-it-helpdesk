import sqlite3
import uuid
from datetime import datetime, timezone

import pytest

from helpdesk import create_app
from helpdesk.db import SAMPLE_TICKET_COUNT, TECHNICIANS, get_db


def test_pages_and_health_of_seed_data(client):
    assert client.get("/").status_code == 200
    assert client.get("/tickets/new").status_code == 200
    tickets = client.get("/api/tickets").get_json()["tickets"]
    assert len(tickets) >= SAMPLE_TICKET_COUNT
    assert client.get("/api/technicians").status_code == 200


def test_seeded_fictional_ticket_details_are_accessible(client):
    sample = client.get("/api/tickets").get_json()["tickets"][0]
    response = client.get(f"/api/tickets/{sample['id']}")
    assert response.status_code == 200
    assert response.get_json()["ticket"]["id"] == sample["id"]


def test_initialization_enables_foreign_keys_and_seeds_technicians(app):
    with app.app_context():
        db = get_db()
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        technicians = db.execute("SELECT id, name FROM technicians").fetchall()
        assert len(technicians) == len(TECHNICIANS)
        assert len({row["id"] for row in technicians}) == len(TECHNICIANS)


def test_database_constraints_reject_invalid_values(app):
    with app.app_context():
        db = get_db()
        with pytest.raises(sqlite3.IntegrityError):
            with db:
                db.execute(
                    """
                    INSERT INTO tickets
                        (id, room, device, category, description, priority, status,
                         created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        "Room 1",
                        "Laptop",
                        "Unsupported",
                        "A description longer than ten characters",
                        "Low",
                        "Open",
                        "2026-01-01T00:00:00Z",
                        "2026-01-01T00:00:00Z",
                    ),
                )


def test_foreign_key_constraint_rejects_unknown_technician(app):
    with app.app_context():
        db = get_db()
        sample = db.execute("SELECT id FROM tickets LIMIT 1").fetchone()
        with pytest.raises(sqlite3.IntegrityError):
            with db:
                db.execute(
                    "UPDATE tickets SET technician_id = ? WHERE id = ?",
                    ("missing-technician", sample["id"]),
                )


def test_database_initialization_is_idempotent_and_preserves_tickets(app, tmp_path):
    with app.app_context():
        db = get_db()
        ticket_id = str(uuid.uuid4())
        with db:
            db.execute(
                """
                INSERT INTO tickets
                    (id, room, device, category, description, priority, status, created_at, updated_at)
                VALUES (?, 'Room 9', 'Projector', 'Hardware',
                        'Persist across database initialization.', 'Low', 'Open', 'now', 'now')
                """,
                (ticket_id,),
            )
    create_app({"DATABASE": str(tmp_path / "helpdesk.sqlite3")})
    with app.app_context():
        db = get_db()
        assert db.execute("SELECT count(*) FROM technicians").fetchone()[0] == len(TECHNICIANS)
        assert db.execute("SELECT count(*) FROM tickets").fetchone()[0] >= SAMPLE_TICKET_COUNT + 1
        assert db.execute("SELECT 1 FROM tickets WHERE id = ?", (ticket_id,)).fetchone()


def test_new_ticket_has_unique_server_fields_and_trimmed_values(client, valid_ticket):
    first = client.post("/api/tickets", json={**valid_ticket, "room": "  Room 9  "})
    second = client.post("/api/tickets", json=valid_ticket)
    assert first.status_code == second.status_code == 201
    one = first.get_json()["ticket"]
    two = second.get_json()["ticket"]
    assert one["id"] != two["id"]
    assert uuid.UUID(one["id"]).version == 4
    created_at = datetime.fromisoformat(one["created_at"].replace("Z", "+00:00"))
    assert created_at.tzinfo == timezone.utc
    assert one["updated_at"] == one["created_at"]
    assert one["status"] == "Open"
    assert one["room"] == "Room 9"
    assert one["technician_id"] is None
    history = client.get(f"/api/tickets/{one['id']}/history")
    assert history.status_code == 200
    assert history.get_json()["history"] == []


@pytest.mark.parametrize(
    "field",
    ["room", "device", "description", "category", "priority"],
)
def test_ticket_creation_rejects_missing_required_fields(client, valid_ticket, field):
    payload = {key: value for key, value in valid_ticket.items() if key != field}
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 400
    assert response.get_json()["error"]["field"] == field


@pytest.mark.parametrize("field", ["room", "device", "description"])
def test_ticket_creation_rejects_whitespace_only_text(client, valid_ticket, field):
    response = client.post("/api/tickets", json={**valid_ticket, field: " \t \n"})
    assert response.status_code == 400
    assert response.get_json()["error"]["field"] == field


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("category", "Facilities"),
        ("priority", "Urgent"),
        ("status", "Closed"),
    ],
)
def test_server_rejects_unsupported_values(client, valid_ticket, field, value):
    response = client.post("/api/tickets", json={**valid_ticket, field: value})
    assert response.status_code == 400
    assert response.get_json()["error"]["field"] == field


def test_short_description_is_rejected(client, valid_ticket):
    response = client.post("/api/tickets", json={**valid_ticket, "description": "a b c d"})
    assert response.status_code == 400
    assert response.get_json()["error"]["field"] == "description"


def test_client_cannot_override_server_owned_fields(client, valid_ticket):
    response = client.post("/api/tickets", json={**valid_ticket, "status": "Resolved"})
    assert response.status_code == 400


def test_invalid_json_and_non_object_bodies_are_rejected(client):
    invalid_json = client.post("/api/tickets", data="{", content_type="application/json")
    non_object = client.post("/api/tickets", json=["ticket"])
    assert invalid_json.status_code == non_object.status_code == 400


def test_room_search_and_combined_filters(client, create_ticket):
    matching = create_ticket(room="Library 3", category="Network", priority="High")
    create_ticket(room="Library 4", category="Network", priority="Low")
    create_ticket(room="Lab 3", category="Network", priority="High")
    response = client.get(
        "/api/tickets?room=library&category=Network&priority=High&status=Open"
    )
    assert response.status_code == 200
    assert [ticket["id"] for ticket in response.get_json()["tickets"]] == [matching["id"]]


def test_search_filter_rejects_unsupported_filter_values(client):
    response = client.get("/api/tickets?status=Closed")
    assert response.status_code == 400
    assert response.get_json()["error"]["field"] == "status"


def test_status_endpoint_rejects_unsupported_status(client, create_ticket):
    ticket = create_ticket()
    response = client.patch(
        f"/api/tickets/{ticket['id']}/status", json={"status": "Closed"}
    )
    assert response.status_code == 400
    assert response.get_json()["error"]["field"] == "status"


def test_ticket_details_reject_malformed_and_nonexistent_ids(client):
    malformed = client.get("/api/tickets/not-a-uuid")
    missing = client.get(f"/api/tickets/{uuid.uuid4()}")
    assert malformed.status_code == 400
    assert malformed.get_json()["error"]["field"] == "ticket_id"
    assert missing.status_code == 404


def test_ticket_details_return_complete_ticket(client, create_ticket):
    created = create_ticket()
    response = client.get(f"/api/tickets/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["ticket"]["description"] == created["description"]


def test_ticket_history_returns_status_transitions_in_order(client, create_ticket):
    ticket = create_ticket()
    client.patch(
        f"/api/tickets/{ticket['id']}/status", json={"status": "In Progress"}
    )
    client.patch(
        f"/api/tickets/{ticket['id']}/status",
        json={"status": "Resolved", "resolution_notes": "Replaced the display cable."},
    )

    response = client.get(f"/api/tickets/{ticket['id']}/history")

    assert response.status_code == 200
    history = response.get_json()["history"]
    assert [(event["old_status"], event["new_status"]) for event in history] == [
        ("Open", "In Progress"),
        ("In Progress", "Resolved"),
    ]
    assert all(event["changed_at"] for event in history)


def test_ticket_history_rejects_malformed_and_nonexistent_ids(client):
    malformed = client.get("/api/tickets/not-a-uuid/history")
    missing = client.get(f"/api/tickets/{uuid.uuid4()}/history")

    assert malformed.status_code == 400
    assert malformed.get_json()["error"]["field"] == "ticket_id"
    assert missing.status_code == 404


def test_assignment_persists_and_can_be_cleared(client, create_ticket):
    ticket = create_ticket()
    assigned = client.patch(
        f"/api/tickets/{ticket['id']}/assignment",
        json={"technician_id": TECHNICIANS[0][0]},
    )
    assert assigned.status_code == 200
    assert assigned.get_json()["ticket"]["assigned_technician"] == TECHNICIANS[0][1]
    cleared = client.patch(
        f"/api/tickets/{ticket['id']}/assignment", json={"technician_id": None}
    )
    assert cleared.status_code == 200
    assert cleared.get_json()["ticket"]["technician_id"] is None


def test_invalid_assignment_does_not_change_saved_assignment(client, create_ticket):
    ticket = create_ticket()
    client.patch(
        f"/api/tickets/{ticket['id']}/assignment",
        json={"technician_id": TECHNICIANS[0][0]},
    )
    response = client.patch(
        f"/api/tickets/{ticket['id']}/assignment",
        json={"technician_id": "not-a-technician"},
    )
    saved = client.get(f"/api/tickets/{ticket['id']}").get_json()["ticket"]
    assert response.status_code == 400
    assert saved["technician_id"] == TECHNICIANS[0][0]


def test_assignment_rejects_malformed_and_missing_ticket_ids(client):
    malformed = client.patch(
        "/api/tickets/malformed/assignment", json={"technician_id": None}
    )
    missing = client.patch(
        f"/api/tickets/{uuid.uuid4()}/assignment", json={"technician_id": None}
    )
    assert malformed.status_code == 400
    assert missing.status_code == 404


def test_status_workflow_and_resolution_metadata(client, create_ticket):
    ticket = create_ticket()
    assigned = client.patch(
        f"/api/tickets/{ticket['id']}/assignment",
        json={"technician_id": TECHNICIANS[0][0]},
    )
    assert assigned.status_code == 200
    in_progress = client.patch(
        f"/api/tickets/{ticket['id']}/status", json={"status": "In Progress"}
    )
    assert in_progress.status_code == 200
    resolved = client.patch(
        f"/api/tickets/{ticket['id']}/status",
        json={"status": "Resolved", "resolution_notes": "Replaced the display cable."},
    )
    assert resolved.status_code == 200
    saved = resolved.get_json()["ticket"]
    assert saved["status"] == "Resolved"
    assert saved["resolution_notes"] == "Replaced the display cable."
    assert saved["resolved_at"]
    assert saved["technician_id"] == TECHNICIANS[0][0]
    with client.application.app_context():
        history = get_db().execute(
            "SELECT count(*) FROM ticket_status_history WHERE ticket_id = ?",
            (ticket["id"],),
        ).fetchone()[0]
    assert history == 2


@pytest.mark.parametrize("notes", [None, "", "   "])
def test_resolution_requires_nonempty_notes(client, create_ticket, notes):
    ticket = create_ticket()
    client.patch(f"/api/tickets/{ticket['id']}/status", json={"status": "In Progress"})
    payload = {"status": "Resolved"}
    if notes is not None:
        payload["resolution_notes"] = notes
    response = client.patch(f"/api/tickets/{ticket['id']}/status", json=payload)
    saved = client.get(f"/api/tickets/{ticket['id']}").get_json()["ticket"]
    assert response.status_code == 400
    assert saved["status"] == "In Progress"
    assert saved["resolution_notes"] is None


@pytest.mark.parametrize(
    ("initial", "target"),
    [
        ("Open", "Resolved"),
        ("Open", "Open"),
        ("In Progress", "Open"),
        ("Resolved", "Open"),
    ],
)
def test_invalid_status_transitions_are_rejected(client, create_ticket, initial, target):
    ticket = create_ticket()
    if initial != "Open":
        client.patch(
            f"/api/tickets/{ticket['id']}/status", json={"status": "In Progress"}
        )
    if initial == "Resolved":
        client.patch(
            f"/api/tickets/{ticket['id']}/status",
            json={"status": "Resolved", "resolution_notes": "The issue has been fixed."},
        )
    response = client.patch(
        f"/api/tickets/{ticket['id']}/status", json={"status": target}
    )
    saved = client.get(f"/api/tickets/{ticket['id']}").get_json()["ticket"]
    assert response.status_code == 400
    assert saved["status"] == initial


def test_resolution_transaction_rolls_back_if_history_write_fails(client, app, create_ticket):
    ticket = create_ticket()
    client.patch(f"/api/tickets/{ticket['id']}/status", json={"status": "In Progress"})
    with app.app_context():
        get_db().execute(
            """
            CREATE TRIGGER reject_status_history BEFORE INSERT ON ticket_status_history
            BEGIN SELECT RAISE(ABORT, 'test failure'); END
            """
        )
    response = client.patch(
        f"/api/tickets/{ticket['id']}/status",
        json={"status": "Resolved", "resolution_notes": "This resolution must roll back."},
    )
    saved = client.get(f"/api/tickets/{ticket['id']}").get_json()["ticket"]
    assert response.status_code == 500
    assert saved["status"] == "In Progress"
    assert saved["resolution_notes"] is None
    assert saved["resolved_at"] is None


def test_ticket_database_write_failure_is_reported_without_saving(
    client, app, valid_ticket
):
    with app.app_context():
        get_db().execute(
            """
            CREATE TRIGGER reject_ticket BEFORE INSERT ON tickets
            WHEN NEW.room = 'Fail'
            BEGIN SELECT RAISE(ABORT, 'test failure'); END
            """
        )
    response = client.post("/api/tickets", json={**valid_ticket, "room": "Fail"})
    assert response.status_code == 500
    assert response.get_json()["error"]["code"] == "database_error"
    results = client.get("/api/tickets?room=Fail").get_json()["tickets"]
    assert results == []


def test_saved_ticket_survives_application_restart(tmp_path, valid_ticket):
    database = str(tmp_path / "restart.sqlite3")
    first_app = create_app({"TESTING": True, "DATABASE": database})
    response = first_app.test_client().post("/api/tickets", json=valid_ticket)
    ticket_id = response.get_json()["ticket"]["id"]
    second_app = create_app({"TESTING": True, "DATABASE": database})
    saved = second_app.test_client().get(f"/api/tickets/{ticket_id}")
    assert saved.status_code == 200
    assert saved.get_json()["ticket"]["description"] == valid_ticket["description"]
