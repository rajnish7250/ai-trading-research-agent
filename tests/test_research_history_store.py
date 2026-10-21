
import json

from services import research_history_store as history_store


def test_save_and_retrieve_research(monkeypatch, tmp_path):
    monkeypatch.setattr(
        history_store,
        "DB_PATH",
        tmp_path / "test_history.db",
    )

    result = {
        "price": {"symbol": "BTC-USD", "value": 65000},
        "report": "Example market research report",
    }

    record_id = history_store.save_research(
        user_id="alice@example.com",
        query="Research Bitcoin",
        result=result,
    )

    history = history_store.get_research_history(
        user_id="alice@example.com"
    )

    assert record_id == 1
    assert len(history) == 1
    assert history[0]["query"] == "Research Bitcoin"
    assert history[0]["result"] == result
    assert history[0]["created_at"]


def test_history_persists_across_database_reopens(monkeypatch, tmp_path):
    db_path = tmp_path / "persistent_history.db"
    monkeypatch.setattr(history_store, "DB_PATH", db_path)

    history_store.save_research(
        user_id="alice@example.com",
        query="Research Ethereum",
        result={"report": "Ethereum report"},
    )

    # Simulate a fresh database connection and retrieval.
    history = history_store.get_research_history(
        user_id="alice@example.com"
    )

    assert len(history) == 1
    assert history[0]["query"] == "Research Ethereum"
    assert history[0]["result"]["report"] == "Ethereum report"


def test_users_cannot_retrieve_each_others_history(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        history_store,
        "DB_PATH",
        tmp_path / "isolated_history.db",
    )

    history_store.save_research(
        user_id="alice@example.com",
        query="Alice's private research",
        result={"report": "Alice's report"},
    )

    history_store.save_research(
        user_id="bob@example.com",
        query="Bob's private research",
        result={"report": "Bob's report"},
    )

    alice_history = history_store.get_research_history(
        user_id="alice@example.com"
    )
    bob_history = history_store.get_research_history(
        user_id="bob@example.com"
    )

    assert len(alice_history) == 1
    assert alice_history[0]["query"] == "Alice's private research"
    assert all(
        "Bob" not in json.dumps(record)
        for record in alice_history
    )

    assert len(bob_history) == 1
    assert bob_history[0]["query"] == "Bob's private research"
    assert all(
        "Alice" not in json.dumps(record)
        for record in bob_history
    )
