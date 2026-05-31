from state.market_state import MarketState
from agents.market_agent import structured_llm

#Creating Sentiment node
def sentiment_node(state:MarketState):
    messages=state["messages"]
    
    latest_message = messages[-1].content
    result=structured_llm.invoke(
        f"""
        Analyze market sentiment from this text:
        
        {latest_message}"""
    )
    
    return {
        "sentiment":result
    }
    