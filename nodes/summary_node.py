from state.market_state import MarketState
def summary_node(state:MarketState):
    news = state.get("news_summary","")
    sentiment = state.get("sentiment","")
    risk= state.get("risk_analysis","")
    
    research_summary = f"""
    NEWS:
    {news}
    
    SENTIMENT: 
    {sentiment}
    
    RISK:
    {risk}
    """
    
    return {
        "research_summary": research_summary,
        "final_response": research_summary
    }