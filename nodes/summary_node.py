from state.market_state import MarketState
from state.schemas import ResearchReport
from agents.specialized_agents import summary_llm


structured_summary_llm = summary_llm.with_structured_output(
    ResearchReport
)


def summary_node(state: MarketState):

    news = state.get("news_summary")
    sentiment = state.get("sentiment")
    risk = state.get("risk_analysis")
    price_data = state.get("market_price_data", "")

    prompt = f"""
    You are a senior market research analyst.

    Synthesize the following structured research results into
    one clear and balanced market research report.

    CURRENT MARKET DATA:
    {price_data}

    NEWS ANALYSIS:
    {news.model_dump()}

    SENTIMENT ANALYSIS:
    {sentiment.model_dump()}

    RISK ANALYSIS:
    {risk.model_dump()}

    Requirements:

    1. Provide a concise executive summary.
    2. Explain the current market outlook.
    3. Highlight the most important developments.
    4. Summarize the sentiment and its main drivers.
    5. Summarize the major risks.
    6. Identify important signals to monitor.
    7. Do not invent facts that are not present in the supplied data.
    8. Do not provide personalized financial advice or guaranteed predictions.

    Return the structured research report.
    """

    response = structured_summary_llm.invoke(prompt)

    print("\nRESEARCH SYNTHESIZER OUTPUT:\n")
    print(response)

    final_response = f"""
# Market Research Report

## Executive Summary
{response.executive_summary}

## Market Outlook
{response.market_outlook}

## Key Developments
{chr(10).join("- " + item for item in response.key_developments)}

## Sentiment
{response.sentiment_summary}

## Risks
{response.risk_summary}

## Watch Items
{chr(10).join("- " + item for item in response.watch_items)}
"""

    return {
        "research_summary": response,
        "final_response": final_response
    }