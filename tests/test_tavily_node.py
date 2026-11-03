
from unittest.mock import MagicMock, patch

import pytest

from nodes.tavily_node import tavily_node


@pytest.fixture
def state():
    return {
        "messages": [
            MagicMock(content="Latest Bitcoin news")
        ]
    }


def test_tavily_node_returns_market_news(state):
    mock_results = [
        {"title": "Bitcoin ETF Update", "content": "ETF developments"}
    ]

    mock_tool = MagicMock()
    mock_tool.invoke.return_value = mock_results

    with patch("nodes.tavily_node.search_tool", mock_tool):
        result = tavily_node(state)

    assert result["market_news"] == str(mock_results)
    mock_tool.invoke.assert_called_once()


def test_tavily_node_handles_empty_results(state):
    mock_tool = MagicMock()
    mock_tool.invoke.return_value = []

    with patch("nodes.tavily_node.search_tool", mock_tool):
        result = tavily_node(state)

    assert result["market_news"] == "[]"


def test_tavily_node_reraises_search_exception(state):
    mock_tool = MagicMock()
    mock_tool.invoke.side_effect = RuntimeError(
        "Search service unavailable"
    )

    with patch("nodes.tavily_node.search_tool", mock_tool):
        with pytest.raises(
            RuntimeError,
            match="Search service unavailable",
        ):
            tavily_node(state)
