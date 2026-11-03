
from unittest.mock import MagicMock, patch

import pytest

from nodes.sentiment_node import sentiment_node


@pytest.fixture
def state():
    return {
        "messages": [
            MagicMock(content="Analyze Bitcoin market sentiment")
        ],
        "retrieved_context": "Historical Bitcoin information",
        "market_news": "Latest Bitcoin market developments",
        "market_price_data": "BTC price: 80000",
    }


@patch("nodes.sentiment_node.structured_sentiment_llm")
def test_sentiment_node_returns_sentiment(mock_llm, state):
    mock_response = {
        "sentiment": "Bullish",
        "confidence": "High",
    }

    mock_llm.invoke.return_value = mock_response

    result = sentiment_node(state)

    assert result["sentiment"] == mock_response
    mock_llm.invoke.assert_called_once()


@patch("nodes.sentiment_node.structured_sentiment_llm")
def test_sentiment_node_reraises_llm_exception(mock_llm, state):
    mock_llm.invoke.side_effect = RuntimeError(
        "Sentiment LLM unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="Sentiment LLM unavailable",
    ):
        sentiment_node(state)
