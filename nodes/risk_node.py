#Creating risk node
from state.market_state import MarketState
from agents.specialized_agents import (risk_llm, RISK_AGENT_PROMPT)

def risk_agent_node(state:MarketState):
    news_summary=state.get("news_summary","")
    sentiment=state.get("sentiment","")
    
    print(news_summary)
    print(sentiment)
    
    return { "risk_analysis": "Low Risk" }
