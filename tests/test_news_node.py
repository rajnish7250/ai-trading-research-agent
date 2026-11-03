
from unittest.mock import MagicMock, patch

import pytest

from nodes.news_node import news_agent_node


@pytest.fixture
def state():
    return {
        "messages": [
            MagicMock(content="Latest Bitcoin market news")
        ],
        "retrieved_context": "Historical Bitcoin market information",
        "market_news": "Latest Bitcoin ETF developments",
        "market_price_data": "BTC price: 80000",
    }


@patch("nodes.news_node.structured_news_llm")
def test_news_agent_node_returns_summary(mock_llm, state):
    mock_response = {"key_developments": ["Bitcoin ETF update"]}
    mock_llm.invoke.return_value = mock_response

    result = news_agent_node(state)

    assert result["news_summary"] == mock_response
    mock_llm.invoke.assert_called_once()


@patch("nodes.news_node.structured_news_llm")
def test_news_agent_node_reraises_llm_exception(mock_llm, state):
    mock_llm.invoke.side_effect = RuntimeError(
        "LLM service unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="LLM service unavailable",
    ):
        news_agent_node(state)
