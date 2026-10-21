
from unittest.mock import Mock

import nodes.retriever_node as retriever_module


def test_retriever_filters_by_user_and_asset(monkeypatch):
    mock_db = Mock()
    mock_db.max_marginal_relevance_search.return_value = []

    monkeypatch.setattr(
        retriever_module,
        "get_vector_db",
        lambda: mock_db,
    )
    monkeypatch.setattr(
        retriever_module,
        "detect_symbol",
        lambda query: "BTC-USD",
    )

    result = retriever_module.retriever_node(
        {
            "user_id": "alice@example.com",
            "messages": [Mock(content="Analyze Bitcoin")],
        }
    )

    assert result["retrieved_context"] == ""

    kwargs = mock_db.max_marginal_relevance_search.call_args.kwargs

    assert kwargs["filter"] == {
        "$and": [
            {"user_id": "alice@example.com"},
            {"asset": "BTC-USD"},
        ]
    }


def test_retriever_does_not_search_without_user_id(monkeypatch):
    mock_db = Mock()

    monkeypatch.setattr(
        retriever_module,
        "get_vector_db",
        lambda: mock_db,
    )

    result = retriever_module.retriever_node(
        {"messages": [Mock(content="Analyze Bitcoin")]}
    )

    assert result["retrieved_context"] == ""
    mock_db.max_marginal_relevance_search.assert_not_called()
