#Create news node
from agents.specialized_agents import news_llm, NEWS_AGENT_PROMPT
from state.market_state import MarketState
def news_agent_node(state:MarketState):
    news_summary = state.get("news_summary","")
    response = news_llm.invoke()
    