#memory_writer_node.py

import logging
import time

from langchain_core.documents import Document
from state.market_state import MarketState
from memory.vector_store import get_vector_db
from memory.text_splitter import split_summary
from utils.asset_mapper import detect_symbol

logger = logging.getLogger(__name__)


def memory_writer_node(state: MarketState):
    start_time = time.perf_counter()

    logger.info("Memory writer node started")

    def log_skip(reason: str, **details):
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        detail_message = " | ".join(
            f"{key}={value}" for key, value in details.items()
        )

        logger.info(
            "Memory writer skipped | reason=%s | %s"
            "duration_ms=%s",
            reason,
            detail_message + " | " if detail_message else "",
            duration_ms,
        )

    try:
        response = state.get("memory_summary", "")
        approved = state.get("memory_approved", False)
        user_id = state.get("user_id")

        if not user_id:
            log_skip("missing_user_id")
            return {"memory_saved": False}

        if not response:
            log_skip("empty_memory_summary")
            return {"memory_saved": False}

        if not approved:
            log_skip("memory_not_approved")
            return {"memory_saved": False}

        messages = state.get("messages", [])

        if not messages:
            log_skip("missing_messages")
            return {"memory_saved": False}

        query = messages[-1].content

        metadata = {
            "source": "agent_generated",
            "type": "research_memory",
            "user_id": user_id,
            "query": query,
            "asset": detect_symbol(query) or "unknown",
        }

        chunks = split_summary(response, metadata)

        if not chunks:
            log_skip("no_chunks_generated")
            return {"memory_saved": False}

        vector_db = get_vector_db()
        vector_db.add_documents(chunks)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Memory writer completed | chunks_saved=%s | "
            "duration_ms=%s",
            len(chunks),
            duration_ms,
        )

        return {"memory_saved": True}

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "Memory writer failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise
