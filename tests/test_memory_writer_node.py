
from unittest.mock import MagicMock, patch

import pytest

from nodes.memory_writer_node import memory_writer_node


@pytest.fixture
def valid_state():
    message = MagicMock()
    message.content = "Research Bitcoin market developments."

    return {
        "memory_summary": "- Bitcoin ETF adoption increased.",
        "memory_approved": True,
        "user_id": "test-user",
        "messages": [message],
    }


def test_memory_writer_rejects_missing_user_id(valid_state):
    valid_state.pop("user_id")

    result = memory_writer_node(valid_state)

    assert result == {"memory_saved": False}


def test_memory_writer_rejects_empty_summary(valid_state):
    valid_state["memory_summary"] = ""

    result = memory_writer_node(valid_state)

    assert result == {"memory_saved": False}


def test_memory_writer_rejects_unapproved_memory(valid_state):
    valid_state["memory_approved"] = False

    result = memory_writer_node(valid_state)

    assert result == {"memory_saved": False}


def test_memory_writer_rejects_missing_messages(valid_state):
    valid_state["messages"] = []

    result = memory_writer_node(valid_state)

    assert result == {"memory_saved": False}


@patch("nodes.memory_writer_node.get_vector_db")
@patch("nodes.memory_writer_node.split_summary")
def test_memory_writer_saves_memory(
    mock_split_summary,
    mock_get_db,
    valid_state,
):
    mock_chunks = [MagicMock(), MagicMock()]
    mock_split_summary.return_value = mock_chunks

    mock_db = MagicMock()
    mock_get_db.return_value = mock_db

    result = memory_writer_node(valid_state)

    assert result == {"memory_saved": True}

    mock_split_summary.assert_called_once()

    metadata = mock_split_summary.call_args.args[1]

    assert metadata["source"] == "agent_generated"
    assert metadata["type"] == "research_memory"
    assert metadata["user_id"] == "test-user"
    assert metadata["query"] == "Research Bitcoin market developments."
    assert metadata["asset"] == "BTC-USD"

    mock_db.add_documents.assert_called_once_with(mock_chunks)


@patch("nodes.memory_writer_node.get_vector_db")
@patch("nodes.memory_writer_node.split_summary")
def test_memory_writer_skips_empty_chunks(
    mock_split_summary,
    mock_get_db,
    valid_state,
):
    mock_split_summary.return_value = []

    result = memory_writer_node(valid_state)

    assert result == {"memory_saved": False}
    mock_get_db.assert_not_called()


@patch("nodes.memory_writer_node.get_vector_db")
@patch("nodes.memory_writer_node.split_summary")
def test_memory_writer_reraises_database_exception(
    mock_split_summary,
    mock_get_db,
    valid_state,
):
    mock_split_summary.return_value = [MagicMock()]

    mock_db = MagicMock()
    mock_db.add_documents.side_effect = RuntimeError(
        "ChromaDB unavailable"
    )
    mock_get_db.return_value = mock_db

    with pytest.raises(RuntimeError, match="ChromaDB unavailable"):
        memory_writer_node(valid_state)
