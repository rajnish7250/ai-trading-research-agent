
from unittest.mock import MagicMock, patch

import pytest

from nodes.memory_compression_node import memory_compression_node


def test_memory_compression_skips_unapproved_memory():
    state = {
        "memory_approved": False,
        "memory_text": "Some market research content",
    }

    result = memory_compression_node(state)

    assert result == {"memory_summary": ""}


def test_memory_compression_skips_missing_memory_text():
    state = {
        "memory_approved": True,
        "memory_text": "",
    }

    result = memory_compression_node(state)

    assert result == {"memory_summary": ""}


@patch("nodes.memory_compression_node.compression_llm")
def test_memory_compression_success(mock_llm):
    mock_response = MagicMock()
    mock_response.content = (
        "- Bitcoin ETF adoption increased.\n"
        "- Regulatory developments affected market structure."
    )

    mock_llm.invoke.return_value = mock_response

    state = {
        "memory_approved": True,
        "memory_text": "A detailed market research report.",
    }

    result = memory_compression_node(state)

    assert result["memory_summary"] == mock_response.content
    mock_llm.invoke.assert_called_once()


@patch("nodes.memory_compression_node.compression_llm")
def test_memory_compression_reraises_llm_exception(mock_llm):
    mock_llm.invoke.side_effect = RuntimeError(
        "LLM service unavailable"
    )

    state = {
        "memory_approved": True,
        "memory_text": "A detailed market research report.",
    }

    with pytest.raises(
        RuntimeError,
        match="LLM service unavailable",
    ):
        memory_compression_node(state)
