import logging

from langchain_core.messages import HumanMessage
from graphs.market_graph import graph

logger = logging.getLogger(__name__)


def perform_research(query: str, user_id: str):
    logger.info("Starting market research")

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

    logger.info("Market research completed")
    return result