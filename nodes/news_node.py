#Create news node
from agents.specialized_agents import news_llm, NEWS_AGENT_PROMPT
from state.market_state import MarketState
from state.schemas import MarketNews
structured_news_llm = news_llm.with_structured_output(
    MarketNews
)

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
    
    Tavily/ Latest Market News:
    {market_news}
    
    Current Market Data:
    {market_price_data}
    
    Analyze the available information and organize the important market developments.

    Return:
    - Key market developments
    - Bitcoin ETF-related updates
    - Regulatory updates
    - A concise summary of the available market data
    """
        
    response= structured_news_llm.invoke(prompt)
    print("\n NEWS AGENT OUTPUT: ")
    print(response)
    
    return {
        "news_summary": response 
    }
    