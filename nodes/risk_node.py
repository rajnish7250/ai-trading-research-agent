#Creating risk node
from state.market_state import MarketState
from agents.specialized_agents import (risk_llm, RISK_AGENT_PROMPT)

def risk_agent_node(state:MarketState):
    user_question = state["messages"][-1].content
    retrieved_context = state.get(
    "retrieved_context",
    "")
    market_news = state.get(
        "market_news",
        ""
    )
    market_price_data = state.get(
        "market_price_data",
        ""
    )
    prompt = f"""
    {RISK_AGENT_PROMPT}
    
    User Question: {user_question}
    Historical Context: {retrieved_context}
    Latest Market News: {market_news}
    Current Market Data: {market_price_data}
    
    Analyze the trading Risks only.
    
    Return:
    -Sentiment
    -Confidence
    -Reasoning
    """
    
    response= risk_llm.invoke(prompt)
    print("\nRISK AGENT OUTPUT\n")
    print(response.content)
    return{
        "risk_analysis": response.content
    }

