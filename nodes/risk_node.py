#Creating risk node
from state.market_state import MarketState
from state.schemas import MarketRisk
from agents.specialized_agents import (risk_llm, RISK_AGENT_PROMPT)

structured_risk_llm = risk_llm.with_structured_output(
    MarketRisk
)
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
    
    Analyze the market Risks using only the information provided. 
    
    Return:
    -Overall Risk Assessment
    -Major Risks and Uncertainties
    -One important signal to monitor
    """
    
    response= structured_risk_llm.invoke(prompt)
    print("\nRISK AGENT OUTPUT\n")
    print(response)
    return{
        "risk_analysis": response
    }

