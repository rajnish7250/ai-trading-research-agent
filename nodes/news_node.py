#Create news node
from agents.specialized_agents import news_llm, NEWS_AGENT_PROMPT
from state.market_state import MarketState
def news_agent_node(state:MarketState):
    user_question = state["messages"][-1].content
    # print("\nUser Question: ")
    # print(user_question)
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
    {NEWS_AGENT_PROMPT}
    
    User Question:
    {user_question}
    
    Historical Context:
    {retrieved_context}
    
    Latest Market News:
    {market_news}
    
    Current Market Data:
    {market_price_data}
    
    Produce a factual market news briefing.
    
    Output sections:
    
    1. Key Developments
    2. ETF Updates
    3. Regulatory Updates
    4. Current Market Data
    
    Do not include sentiment.
    Do not include risk.
    """
        
    response= news_llm.invoke(prompt)
    print("\n NEWS AGENT OUTPUT: ")
    print(response.content)
    
    return {
        "news_summary": response.content 
    }
    