
from fastapi.testclient import TestClient
from main import app
from auth.jwt_handler import create_access_token

client = TestClient(app)


def mock_research(monkeypatch):
    """Replace the real research workflow with a predictable result."""
    monkeypatch.setattr(
        "main.perform_research",
        lambda query, user_id: {
            "market_price_data": "Mock price",
            "news_summary": "Mock news",
            "sentiment": "Bullish",
            "risk_analysis": "Moderate risk",
            "final_response": "Mock research report",
        },
    )


def authenticate_as(monkeypatch, email):
    """Create a valid test token for an existing test user."""
    monkeypatch.setattr(
        "auth.dependencies.get_user",
        lambda requested_email: {"email": requested_email},
    )

    token = create_access_token({"sub": email})
    return {"Authorization": f"Bearer {token}"}


def test_research_requires_authentication():
    response = client.post(
        "/research",
        json={"query": "Analyze BTC-USD"},
    )

    assert response.status_code == 401


def test_research_rejects_invalid_token():
    response = client.post(
        "/research",
        json={"query": "Analyze BTC-USD"},
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_research_accepts_valid_token(monkeypatch, tmp_path):
    from services import research_history_store

    monkeypatch.setattr(
        research_history_store,
        "DB_PATH",
        tmp_path / "research.db",
    )
    mock_research(monkeypatch)
    headers = authenticate_as(monkeypatch, "test@example.com")

    response = client.post(
        "/research",
        json={"query": "Analyze BTC-USD"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["report"] == "Mock research report"

    history_response = client.get(
        "/research/history",
        headers=headers,
    )

    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["query"] == "Analyze BTC-USD"
    assert history[0]["result"]["report"] == "Mock research report"


def test_research_history_requires_authentication():
    response = client.get("/research/history")

    assert response.status_code == 401


def test_research_history_is_isolated_by_user(monkeypatch, tmp_path):
    from services import research_history_store

    monkeypatch.setattr(
        research_history_store,
        "DB_PATH",
        tmp_path / "isolated_research.db",
    )

    research_history_store.save_research(
        user_id="alice@example.com",
        query="Alice private query",
        result={"report": "Alice private report"},
    )
    research_history_store.save_research(
        user_id="bob@example.com",
        query="Bob private query",
        result={"report": "Bob private report"},
    )

    alice_headers = authenticate_as(
        monkeypatch, "alice@example.com"
    )
    alice_response = client.get(
        "/research/history",
        headers=alice_headers,
    )

    assert alice_response.status_code == 200
    alice_history = alice_response.json()
    assert len(alice_history) == 1
    assert alice_history[0]["query"] == "Alice private query"
    assert alice_history[0]["result"]["report"] == "Alice private report"

    bob_headers = authenticate_as(
        monkeypatch, "bob@example.com"
    )
    bob_response = client.get(
        "/research/history",
        headers=bob_headers,
    )

    assert bob_response.status_code == 200
    bob_history = bob_response.json()
    assert len(bob_history) == 1
    assert bob_history[0]["query"] == "Bob private query"
    assert bob_history[0]["result"]["report"] == "Bob private report"
