
from unittest.mock import MagicMock, patch

import pytest

from nodes.memory_filter_node import memory_filter_node


@pytest.fixture
def state():
    report = MagicMock()

    report.executive_summary = "Bitcoin market shows significant developments."
    report.market_outlook = "The outlook remains cautiously positive."
    report.key_developments = ["ETF inflows increased."]
    report.sentiment_summary = "Bullish sentiment."
    report.risk_summary = "Regulatory uncertainty remains."
    report.watch_items = ["ETF inflows"]

    return {
        "user_id": "test-user",
        "research_summary": report,
    }


def test_memory_filter_rejects_missing_user_id(state):
    state.pop("user_id")

    result = memory_filter_node(state)

    assert result == {
        "memory_approved": False,
        "memory_text": "",
    }


def test_memory_filter_rejects_missing_report():
    state = {
        "user_id": "test-user",
        "research_summary": None,
    }

    result = memory_filter_node(state)

    assert result == {
        "memory_approved": False,
        "memory_text": "",
    }


@patch("nodes.memory_filter_node.get_vector_db")
def test_memory_filter_approves_new_memory(mock_get_db, state):
    mock_db = MagicMock()
    mock_db.similarity_search_with_score.return_value = []

    mock_get_db.return_value = mock_db

    result = memory_filter_node(state)

    assert result["memory_approved"] is True
    assert len(result["memory_text"]) >= 100

    mock_db.similarity_search_with_score.assert_called_once()

    call_kwargs = (
        mock_db.similarity_search_with_score.call_args.kwargs
    )

    assert call_kwargs["filter"] == {"user_id": "test-user"}


@patch("nodes.memory_filter_node.get_vector_db")
def test_memory_filter_rejects_duplicate_memory(mock_get_db, state):
    mock_db = MagicMock()

    mock_db.similarity_search_with_score.return_value = [
        (MagicMock(), 0.1)
    ]

    mock_get_db.return_value = mock_db

    result = memory_filter_node(state)

    assert result == {
        "memory_approved": False,
        "memory_text": "",
    }


@patch("nodes.memory_filter_node.get_vector_db")
def test_memory_filter_reraises_database_exception(
    mock_get_db,
    state,
):
    mock_db = MagicMock()

    mock_db.similarity_search_with_score.side_effect = RuntimeError(
        "Vector database unavailable"
    )

    mock_get_db.return_value = mock_db

    with pytest.raises(
        RuntimeError,
        match="Vector database unavailable",
    ):
        memory_filter_node(state)
