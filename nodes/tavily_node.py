#tavily_node.py
from state.market_state import MarketState
from tools.market_tools import search_tool


def tavily_node(state: MarketState):

    user_question = state["messages"][-1].content

    search_query = f"""
    Latest market news about:

    {user_question}

    Focus on:
    - Market outlook
    - ETF developments
    - Regulatory developments
    """

    # print("\nTAVILY SEARCH QUERY:\n")
    # print(search_query)

    results = search_tool.invoke(search_query)

    print("\nTAVILY RESULTS:\n Ignoring as of now, because it has very large volume of data. \n")
    # print(results)

    return {
        "market_news": str(results)
    }