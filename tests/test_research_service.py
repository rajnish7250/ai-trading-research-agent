from services import research_service


def test_research_uses_separate_threads_for_users(monkeypatch):
    captured_thread_ids = []

    def mock_invoke(state, config):
        thread_id = config["configurable"]["thread_id"]
        captured_thread_ids.append(thread_id)
        return {"final_response": "Mock report"}

    monkeypatch.setattr(
        research_service.graph,
        "invoke",
        mock_invoke,
    )

    research_service.perform_research(
        query="Analyze BTC-USD",
        user_id="alice@example.com",
    )

    research_service.perform_research(
        query="Analyze ETH-USD",
        user_id="bob@example.com",
    )

    assert captured_thread_ids == [
        "user_alice@example.com",
        "user_bob@example.com",
    ]

    assert captured_thread_ids[0] != captured_thread_ids[1]
    

def test_research_passes_user_id_into_graph_state(monkeypatch):

    captured = {}

    def mock_invoke(state, config):
        captured["state"] = state
        captured["config"] = config
        return {"final_response": "Mock report"}

    monkeypatch.setattr(research_service.graph, "invoke", mock_invoke)

    research_service.perform_research(
        query="Analyze BTC-USD",
        user_id="alice@example.com",
    )

    assert captured["state"]["user_id"] == "alice@example.com"
    assert (
        captured["config"]["configurable"]["thread_id"]
        == "user_alice@example.com"
    )
