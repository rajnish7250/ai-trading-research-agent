from state.market_state import MarketState
from state.schemas import MarketSentiment
from agents.specialized_agents import(sentiment_llm, SENTIMENT_AGENT_PROMPT)
structured_sentiment_llm = sentiment_llm.with_structured_output(
    MarketSentiment
)
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
    
    Analyze the market sentiment using only the information provided.
    
    Return:
    -Overall Sentiment
    -Confidence
    -Top Factors Driving that Sentiment
    """
    
    response = structured_sentiment_llm.invoke(prompt)
    
    print("\nSENTIMENT OUTPUT:\n")
    print(response)
    
    return {
        "sentiment": response
    }