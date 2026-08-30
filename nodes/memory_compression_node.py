from state.market_state import MarketState
from agents.specialized_agents import news_llm as compression_llm

def memory_compression_node(state: MarketState):
    if not state.get("memory_approved", False):
        return {"memory_summary": ""}
    research_summary = state.get("research_summary","")
    prompt = f"""
    Extract ONLY durable market knowledge.

    Store:
    - regulatory developments
    - institutional adoption events
    - ETF launches
    - corporate actions
    - technological developments
    - market structure changes

    DO NOT store:
    - bullish/bearish opinions
    - sentiment
    - confidence scores
    - risk assessments
    - forecasts
    - price predictions

    Output concise bullet points.
    
    Report:

    {research_summary}
    """

    response = compression_llm.invoke(prompt)

    print("\nMEMORY SUMMARY:\n")
    print(response.content)

    return {
        "memory_summary": response.content
    }