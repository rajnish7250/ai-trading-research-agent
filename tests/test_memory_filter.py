from unittest.mock import Mock

import nodes.memory_filter_node as memory_filter_module
from state.schemas import ResearchReport


def test_memory_filter_approves_new_research(monkeypatch):
    report = ResearchReport(
        executive_summary=(
            "Bitcoin ETF inflows have increased, "
            "indicating stronger institutional interest."
        ),
        market_outlook=(
            "The market outlook is cautiously positive "
            "while volatility remains elevated."
        ),
        key_developments=[
            "ETF inflows increased this week.",
            "Trading activity remains elevated.",
        ],
        sentiment_summary="Positive, with moderate confidence.",
        risk_summary="Moderate risk due to market volatility.",
        watch_items=[
            "Monitor ETF flows.",
            "Watch for sudden price reversals.",
        ],
    )

    mock_vector_db = Mock()
    mock_vector_db.similarity_search_with_score.return_value = []

    monkeypatch.setattr(
        memory_filter_module,
        "get_vector_db",
        lambda: mock_vector_db,
    )

    result = memory_filter_module.memory_filter_node(
        {"research_summary": report}
    )

    assert result["memory_approved"] is True
    assert "Bitcoin ETF inflows" in result["memory_text"]
    mock_vector_db.similarity_search_with_score.assert_called_once()
