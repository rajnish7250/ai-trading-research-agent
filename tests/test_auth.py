from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


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
        headers={
            "Authorization": "Bearer invalid.token.value"
        },
    )

    assert response.status_code == 401
    
    
def test_research_accepts_valid_token(monkeypatch):
    from auth.jwt_handler import create_access_token

    # Simulate an existing authenticated user.
    monkeypatch.setattr(
        "auth.dependencies.get_user",
        lambda email: {"email": email},
    )

    # Avoid calling external market-data and LLM services.
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

    token = create_access_token(
        {"sub": "test@example.com"}
    )

    response = client.post(
        "/research",
        json={"query": "Analyze BTC-USD"},
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert response.json()["report"] == "Mock research report"