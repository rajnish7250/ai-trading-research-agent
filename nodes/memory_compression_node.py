
import logging
import time

from state.market_state import MarketState
from agents.specialized_agents import news_llm as compression_llm

logger = logging.getLogger(__name__)


def memory_compression_node(state: MarketState):
    start_time = time.perf_counter()

    logger.info("Memory compression node started")

    def log_skip(reason: str, **details):
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        detail_message = " | ".join(
            f"{key}={value}" for key, value in details.items()
        )

        logger.info(
            "Memory compression skipped | reason=%s | %s"
            "duration_ms=%s",
            reason,
            detail_message + " | " if detail_message else "",
            duration_ms,
        )

    try:
        if not state.get("memory_approved", False):
            log_skip("memory_not_approved")
            return {"memory_summary": ""}

        memory_text = state.get("memory_text", "")

        if not memory_text:
            log_skip("missing_memory_text")
            return {"memory_summary": ""}

        prompt = f"""
        Extract ONLY durable market knowledge.

        Store:
        - regulatory developments
        - institutional adoption events
        - ETF launches
        - corporate actions
        - technological developments
        - market structure changes

        DO NOT store:
        - bullish/bearish opinions
        - sentiment
        - confidence scores
        - risk assessments
        - forecasts
        - price predictions

        Output concise bullet points.

        Report:

        {memory_text}
        """

        response = compression_llm.invoke(prompt)

        memory_summary = response.content

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Memory compression completed | "
            "input_length=%s | output_length=%s | duration_ms=%s",
            len(memory_text),
            len(memory_summary),
            duration_ms,
        )

        return {
            "memory_summary": memory_summary
        }

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "Memory compression failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise
