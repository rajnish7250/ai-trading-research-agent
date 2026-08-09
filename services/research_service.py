import logging
from langchain_core.messages import HumanMessage
from graphs.market_graph import graph
logger = logging.getLogger(__name__)

def perform_research(query: str):
    logger.info("Starting market research")
    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=query)
            ]
        },
        config={
            "configurable": {
                "thread_id": "user_1"
            }
        },
    )

    logger.info("Market research completed")

    return result