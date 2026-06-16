from state.market_state import MarketState
from agents.llm_provider import get_llm
from config import LLM_PROVIDER
llm = get_llm(LLM_PROVIDER)
def memory_compression_node(state: MarketState):
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

    response = llm.invoke(prompt)

    print("\nMEMORY SUMMARY:\n")
    print(response.content)

    return {
        "memory_summary": response.content
    }