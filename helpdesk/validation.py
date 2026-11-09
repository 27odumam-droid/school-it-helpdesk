from uuid import UUID

CATEGORIES = frozenset({"Hardware", "Software", "Network", "Other"})
PRIORITIES = frozenset({"Low", "Medium", "High"})
STATUSES = frozenset({"Open", "In Progress", "Resolved"})
MIN_DESCRIPTION_CHARACTERS = 10
SERVER_OWNED_FIELDS = frozenset(
    {
        "id",
        "status",
        "created_at",
        "updated_at",
        "technician_id",
        "resolution_notes",
        "resolved_at",
    }
)


class ValidationError(ValueError):
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field


def parse_uuid(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError):
        return None
    return str(parsed)


def required_text(payload, field):
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field.replace('_', ' ').capitalize()} is required.", field)
    return value.strip()


def validate_ticket_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object.")
    owned_fields = SERVER_OWNED_FIELDS.intersection(payload)
    if owned_fields:
        field = sorted(owned_fields)[0]
        raise ValidationError(f"{field} is set by the server.", field)

    room = required_text(payload, "room")
    device = required_text(payload, "device")
    description = required_text(payload, "description")
    if len("".join(description.split())) < MIN_DESCRIPTION_CHARACTERS:
        raise ValidationError(
            f"Description must contain at least {MIN_DESCRIPTION_CHARACTERS} non-whitespace characters.",
            "description",
        )

    category = payload.get("category")
    if not isinstance(category, str) or category not in CATEGORIES:
        raise ValidationError("Choose a supported category.", "category")
    priority = payload.get("priority")
    if not isinstance(priority, str) or priority not in PRIORITIES:
        raise ValidationError("Choose a supported priority.", "priority")

    return {
        "room": room,
        "device": device,
        "description": description,
        "category": category,
        "priority": priority,
    }
