import pytest

from helpdesk import create_app


@pytest.fixture
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "helpdesk.sqlite3"),
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_ticket():
    return {
        "room": "Room 212",
        "device": "Teacher laptop",
        "description": "The classroom laptop cannot connect to the display.",
        "category": "Hardware",
        "priority": "Medium",
    }


@pytest.fixture
def create_ticket(client, valid_ticket):
    def create(**overrides):
        response = client.post("/api/tickets", json={**valid_ticket, **overrides})
        assert response.status_code == 201
        return response.get_json()["ticket"]

    return create
