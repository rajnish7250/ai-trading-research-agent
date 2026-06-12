from state.market_state import MarketState
from agents.market_agent import structured_llm

#Creating Sentiment node
def sentiment_node(state:MarketState):
    
    news_summary=state.get("news_summary","")
    print(f"Sentiment Received: {news_summary}")
    
    return {
        "sentiment": "Positive"
    }
    