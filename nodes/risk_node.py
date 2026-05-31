#Creating risk node
from state.market_state import MarketState
from agents.specialized_agents import (risk_llm, RISK_AGENT_PROMPT)

def risk_agent_node(state:MarketState):
    news=state.get("news_summary","")
    response=risk_llm.invoke(
        f"""
        {RISK_AGENT_PROMPT}
        Market News:
        {news}
        Analyze risks and uncertainity"""
    )
    
    return {
        "risk_analysis":response.content
    }
