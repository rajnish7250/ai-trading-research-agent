
from unittest.mock import Mock

import nodes.memory_writer_node as writer_module


def test_memory_writer_saves_user_id_in_metadata(monkeypatch):
    mock_db = Mock()

    monkeypatch.setattr(
        writer_module,
        "get_vector_db",
        lambda: mock_db,
    )
    monkeypatch.setattr(
        writer_module,
        "split_summary",
        lambda text, metadata: [Mock(metadata=metadata)],
    )
    monkeypatch.setattr(
        writer_module,
        "detect_symbol",
        lambda query: "BTC-USD",
    )

    result = writer_module.memory_writer_node(
        {
            "user_id": "alice@example.com",
            "memory_summary": "Bitcoin ETF adoption continues to develop.",
            "memory_approved": True,
            "messages": [Mock(content="Analyze BTC-USD")],
        }
    )

    assert result["memory_saved"] is True
    saved_document = mock_db.add_documents.call_args.args[0][0]

    assert saved_document.metadata["user_id"] == "alice@example.com"
    assert saved_document.metadata["asset"] == "BTC-USD"


def test_memory_writer_skips_missing_user(monkeypatch):
    mock_db = Mock()

    monkeypatch.setattr(
        writer_module,
        "get_vector_db",
        lambda: mock_db,
    )

    result = writer_module.memory_writer_node(
        {
            "memory_summary": "Some research memory",
            "memory_approved": True,
            "messages": [Mock(content="Analyze BTC-USD")],
        }
    )

    assert result["memory_saved"] is False
    mock_db.add_documents.assert_not_called()
