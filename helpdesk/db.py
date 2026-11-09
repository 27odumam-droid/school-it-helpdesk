import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app, g

logger = logging.getLogger(__name__)

TECHNICIANS = (
    ("tech-alex", "Alex Rivera"),
    ("tech-jamie", "Jamie Chen"),
    ("tech-morgan", "Morgan Patel"),
    ("tech-taylor", "Taylor Brooks"),
    ("tech-sam", "Sam Nguyen"),
)

SAMPLE_TICKET_NAMESPACE = uuid.UUID("cc6f7d8c-a313-48da-8dcb-f629b3c23bb4")
SAMPLE_TICKET_COUNT = 15
SAMPLE_ROOMS = ("101", "204", "Library", "Gym", "Main Office")
SAMPLE_DEVICES = (
    "Teacher laptop",
    "Projector",
    "Wireless access point",
    "Lab desktop",
    "Document camera",
)
SAMPLE_CATEGORIES = ("Hardware", "Software", "Network", "Other")
SAMPLE_PRIORITIES = ("Low", "Medium", "High")
SAMPLE_STATUSES = ("Open", "In Progress", "Resolved")

SCHEMA = """
CREATE TABLE IF NOT EXISTS technicians (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0)
);
CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    room TEXT NOT NULL CHECK (length(trim(room)) > 0),
    device TEXT NOT NULL CHECK (length(trim(device)) > 0),
    category TEXT NOT NULL CHECK (category IN ('Hardware', 'Software', 'Network', 'Other')),
    description TEXT NOT NULL CHECK (length(trim(description)) >= 10),
    priority TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High')),
    status TEXT NOT NULL CHECK (status IN ('Open', 'In Progress', 'Resolved')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    technician_id TEXT REFERENCES technicians(id),
    resolution_notes TEXT,
    resolved_at TEXT,
    CHECK (
        (status = 'Resolved' AND length(trim(COALESCE(resolution_notes, ''))) > 0
         AND resolved_at IS NOT NULL)
        OR
        (status != 'Resolved' AND resolution_notes IS NULL AND resolved_at IS NULL)
    )
);
CREATE TABLE IF NOT EXISTS ticket_status_history (
    id INTEGER PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    old_status TEXT NOT NULL CHECK (old_status IN ('Open', 'In Progress', 'Resolved')),
    new_status TEXT NOT NULL CHECK (new_status IN ('Open', 'In Progress', 'Resolved')),
    changed_at TEXT NOT NULL,
    CHECK (old_status != new_status)
);
CREATE INDEX IF NOT EXISTS tickets_created_at_idx ON tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS tickets_room_idx ON tickets(room COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS ticket_history_ticket_idx ON ticket_status_history(ticket_id);
"""


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_db():
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        if connection.in_transaction:
            connection.rollback()
        connection.close()


def _sample_tickets():
    for index in range(SAMPLE_TICKET_COUNT):
        status = SAMPLE_STATUSES[index % len(SAMPLE_STATUSES)]
        created_at = f"2026-01-{(index % 28) + 1:02d}T09:00:00Z"
        resolved = status == "Resolved"
        yield (
            str(uuid.uuid5(SAMPLE_TICKET_NAMESPACE, f"sample-ticket-{index + 1}")),
            SAMPLE_ROOMS[index % len(SAMPLE_ROOMS)],
            SAMPLE_DEVICES[index % len(SAMPLE_DEVICES)],
            SAMPLE_CATEGORIES[index % len(SAMPLE_CATEGORIES)],
            f"Fictional sample ticket {index + 1} describes a classroom technology issue.",
            SAMPLE_PRIORITIES[index % len(SAMPLE_PRIORITIES)],
            status,
            created_at,
            created_at,
            TECHNICIANS[index % len(TECHNICIANS)][0] if index % 2 == 0 else None,
            "Fictional sample resolution completed." if resolved else None,
            f"2026-02-{(index % 28) + 1:02d}T10:00:00Z" if resolved else None,
        )


def initialize_database(app):
    database_path = Path(app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.executescript(SCHEMA)
        with connection:
            connection.executemany(
                "INSERT OR IGNORE INTO technicians (id, name) VALUES (?, ?)",
                TECHNICIANS,
            )
            connection.executemany(
                """
                INSERT OR IGNORE INTO tickets
                    (id, room, device, category, description, priority, status,
                     created_at, updated_at, technician_id, resolution_notes, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _sample_tickets(),
            )
    except sqlite3.Error:
        logger.exception("Could not initialize the help desk database")
        raise
    finally:
        connection.close()
