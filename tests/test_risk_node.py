
from unittest.mock import MagicMock, patch

import pytest

from nodes.risk_node import risk_agent_node


@pytest.fixture
def state():
    return {
        "messages": [
            MagicMock(content="Analyze Bitcoin market risks")
        ],
        "retrieved_context": "Historical Bitcoin information",
        "market_news": "Latest Bitcoin regulatory developments",
        "market_price_data": "BTC price: 80000",
    }


@patch("nodes.risk_node.structured_risk_llm")
def test_risk_agent_node_returns_analysis(mock_llm, state):
    mock_response = {
        "overall_risk": "Medium",
        "major_risks": ["Regulatory uncertainty"],
    }

    mock_llm.invoke.return_value = mock_response

    result = risk_agent_node(state)

    assert result["risk_analysis"] == mock_response
    mock_llm.invoke.assert_called_once()


@patch("nodes.risk_node.structured_risk_llm")
def test_risk_agent_node_reraises_llm_exception(mock_llm, state):
    mock_llm.invoke.side_effect = RuntimeError(
        "Risk LLM unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="Risk LLM unavailable",
    ):
        risk_agent_node(state)
