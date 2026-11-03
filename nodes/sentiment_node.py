#sentiment_node.py

import logging
import time

from state.market_state import MarketState
from state.schemas import MarketSentiment
from agents.specialized_agents import (
    sentiment_llm,
    SENTIMENT_AGENT_PROMPT,
)
from agents.llm_provider import get_structured_output_llm

logger = logging.getLogger(__name__)

structured_sentiment_llm = get_structured_output_llm(
    sentiment_llm,
    MarketSentiment,
)


def sentiment_node(state: MarketState):
    start_time = time.perf_counter()

    logger.info("Sentiment agent node started")

    try:
        user_question = state["messages"][-1].content

        retrieved_context = state.get("retrieved_context", "")
        market_news = state.get("market_news", "")
        market_price_data = state.get("market_price_data", "")

        prompt = f"""
        {SENTIMENT_AGENT_PROMPT}

        User Question: {user_question}
        Historical Context: {retrieved_context}
        Latest Market News: {market_news}
        Current Market Data: {market_price_data}

        Analyze the market sentiment using only the information provided.

        Return:
        -Overall Sentiment
        -Confidence
        -Top Factors Driving that Sentiment
        """

        response = structured_sentiment_llm.invoke(prompt)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Sentiment agent node completed | duration_ms=%s",
            duration_ms,
        )

        return {
            "sentiment": response
        }

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "Sentiment agent node failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise
