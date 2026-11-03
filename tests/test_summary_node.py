
from unittest.mock import MagicMock, patch

import pytest

from nodes.summary_node import summary_node


@pytest.fixture
def state():
    news = MagicMock()
    news.model_dump.return_value = {
        "developments": ["Bitcoin ETF update"]
    }

    sentiment = MagicMock()
    sentiment.model_dump.return_value = {
        "sentiment": "Bullish"
    }

    risk = MagicMock()
    risk.model_dump.return_value = {
        "risk": "Medium"
    }

    return {
        "news_summary": news,
        "sentiment": sentiment,
        "risk_analysis": risk,
        "market_price_data": "BTC price: 80000",
    }


@patch("nodes.summary_node.structured_summary_llm")
def test_summary_node_returns_research_report(mock_llm, state):
    mock_response = MagicMock()

    mock_response.executive_summary = "Bitcoin outlook is positive."
    mock_response.market_outlook = "Moderately bullish."
    mock_response.key_developments = ["ETF developments"]
    mock_response.sentiment_summary = "Bullish sentiment."
    mock_response.risk_summary = "Regulatory uncertainty."
    mock_response.watch_items = ["ETF inflows"]

    mock_llm.invoke.return_value = mock_response

    result = summary_node(state)

    assert result["research_summary"] == mock_response
    assert "Market Research Report" in result["final_response"]
    assert "Executive Summary" in result["final_response"]
    assert "Bitcoin outlook is positive." in result["final_response"]

    mock_llm.invoke.assert_called_once()


@patch("nodes.summary_node.structured_summary_llm")
def test_summary_node_reraises_llm_exception(mock_llm, state):
    mock_llm.invoke.side_effect = RuntimeError(
        "Summary LLM unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="Summary LLM unavailable",
    ):
        summary_node(state)
