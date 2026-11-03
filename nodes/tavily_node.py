#tavily_node.py

import logging
import time

from state.market_state import MarketState
from tools.market_tools import search_tool

logger = logging.getLogger(__name__)


def tavily_node(state: MarketState):
    start_time = time.perf_counter()

    logger.info("Tavily node started")

    try:
        user_question = state["messages"][-1].content

        search_query = f"""
        Latest market news about:

        {user_question}

        Focus on:
        - Market outlook
        - ETF developments
        - Regulatory developments
        """

        results = search_tool.invoke(search_query)

        # Calculate the number of returned results without logging their contents.
        if isinstance(results, list):
            result_count = len(results)
        else:
            result_count = None

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Tavily node completed | result_count=%s | duration_ms=%s",
            result_count if result_count is not None else "unknown",
            duration_ms,
        )

        return {
            "market_news": str(results)
        }

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "Tavily node failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise
