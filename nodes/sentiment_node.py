from state.market_state import MarketState
from agents.specialized_agents import(sentiment_llm, SENTIMENT_AGENT_PROMPT)
def sentiment_node(state:MarketState):
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
    {SENTIMENT_AGENT_PROMPT}
    
    User Question: {user_question}
    Historical Context: {retrieved_context}
    Latest Market News: {market_news}
    Current Market Data: {market_price_data}
    
    Analyze the sentiment.
    
    Return:
    -Sentiment
    -Confidence
    -Reasoning
    """
    
    response= sentiment_llm.invoke(prompt)
    print("\nSENTIMENT OUTPUT: \n")
    print(response.content)
    
    return{
        "sentiment": response.content
    }