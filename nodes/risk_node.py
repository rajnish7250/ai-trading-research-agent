#Creating risk node

import logging
import time

from state.market_state import MarketState
from state.schemas import MarketRisk
from agents.specialized_agents import (
    risk_llm,
    RISK_AGENT_PROMPT,
)
from agents.llm_provider import get_structured_output_llm

logger = logging.getLogger(__name__)

structured_risk_llm = get_structured_output_llm(
    risk_llm,
    MarketRisk,
)


def risk_agent_node(state: MarketState):
    start_time = time.perf_counter()

    logger.info("Risk agent node started")

    try:
        user_question = state["messages"][-1].content

        retrieved_context = state.get("retrieved_context", "")
        market_news = state.get("market_news", "")
        market_price_data = state.get("market_price_data", "")

        prompt = f"""
        {RISK_AGENT_PROMPT}

        User Question: {user_question}
        Historical Context: {retrieved_context}
        Latest Market News: {market_news}
        Current Market Data: {market_price_data}

        Analyze the market Risks using only the information provided.

        Return:
        -Overall Risk Assessment
        -Major Risks and Uncertainties
        -One important signal to monitor
        """

        response = structured_risk_llm.invoke(prompt)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Risk agent node completed | duration_ms=%s",
            duration_ms,
        )

        return {
            "risk_analysis": response
        }

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "Risk agent node failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise
