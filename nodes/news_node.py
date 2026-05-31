#Create news node
from agents.specialized_agents import news_llm, NEWS_AGENT_PROMPT
from state.market_state import MarketState
def news_agent_node(state:MarketState):
    messages=state["messages"]
    latest_user_message = messages[0].content
    
    response = news_llm.invoke(
        f"""
        {NEWS_AGENT_PROMPT}
        
        User Request:
        {latest_user_message}
        
        Provide Concise market news summary"""
    )
    
    return {
        "news_summary": response.content
    }