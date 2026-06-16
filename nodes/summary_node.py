from state.market_state import MarketState

def summary_node(state: MarketState):

    news = state.get("news_summary", "")
    sentiment = state.get("sentiment", "")
    risk = state.get("risk_analysis", "")
    price_data = state.get("market_price_data", "")

    research_summary = f"""
NEWS:
{news}

SENTIMENT:
{sentiment}

RISK:
{risk}
"""

    final_response = f"""
# Market Research Report

## Current Price
{price_data}

## Market News
{news}

## Sentiment Analysis
{sentiment}

## Risk Assessment
{risk}
"""

    return {
        "research_summary": research_summary,
        "final_response": final_response
    }