#Create news node

import logging
import time

from agents.specialized_agents import news_llm, NEWS_AGENT_PROMPT
from state.market_state import MarketState
from state.schemas import MarketNews
from agents.llm_provider import get_structured_output_llm

logger = logging.getLogger(__name__)

structured_news_llm = get_structured_output_llm(
    news_llm,
    MarketNews,
)


def news_agent_node(state: MarketState):
    start_time = time.perf_counter()

    logger.info("News agent node started")

    try:
        user_question = state["messages"][-1].content

        retrieved_context = state.get("retrieved_context", "")
        market_news = state.get("market_news", "")
        market_price_data = state.get("market_price_data", "")

        prompt = f"""
        {NEWS_AGENT_PROMPT}

        User Question:
        {user_question}

        Historical Context:
        {retrieved_context}

        Tavily/ Latest Market News:
        {market_news}

        Current Market Data:
        {market_price_data}

        Analyze the available information and organize the important market developments.

        Return:
        - Key market developments
        - Bitcoin ETF-related updates
        - Regulatory updates
        - A concise summary of the available market data
        """

        response = structured_news_llm.invoke(prompt)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "News agent node completed | duration_ms=%s",
            duration_ms,
        )

        return {
            "news_summary": response
        }

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "News agent node failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise

    