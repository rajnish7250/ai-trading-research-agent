
import logging
import time

from langchain_core.messages import HumanMessage
from graphs.market_graph import graph

logger = logging.getLogger(__name__)


def perform_research(query: str, user_id: str):
    start_time = time.perf_counter()

    logger.info("Market research started")

    try:
        result = graph.invoke(
            {
                "messages": [
                    HumanMessage(content=query)
                ],
                "user_id": user_id,
            },
            config={
                "configurable": {
                    "thread_id": f"user_{user_id}"
                }
            },
        )

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Market research completed | duration_ms=%s",
            duration_ms,
        )

        return result

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "Market research failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise
