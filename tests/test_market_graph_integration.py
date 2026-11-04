
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from graphs import market_graph


class GraphState(TypedDict, total=False):
    completed: list[str]


def test_parallel_nodes_wait_for_all_upstream_nodes():
    execution_order = []

    def retriever(state):
        execution_order.append("retriever")
        return {}

    def tavily(state):
        execution_order.append("tavily")
        return {}

    def yfinance(state):
        execution_order.append("yfinance")
        return {}

    def news(state):
        assert {
            "retriever",
            "tavily",
            "yfinance",
        }.issubset(execution_order)

        execution_order.append("news")
        return {}

    def sentiment(state):
        assert {
            "retriever",
            "tavily",
            "yfinance",
        }.issubset(execution_order)

        execution_order.append("sentiment")
        return {}

    def risk(state):
        assert {
            "retriever",
            "tavily",
            "yfinance",
        }.issubset(execution_order)

        execution_order.append("risk")
        return {}

    def summary(state):
        assert {
            "news",
            "sentiment",
            "risk",
        }.issubset(execution_order)

        execution_order.append("summary")
        return {}

    builder = StateGraph(GraphState)

    builder.add_node("retriever", retriever)
    builder.add_node("tavily", tavily)
    builder.add_node("yfinance", yfinance)
    builder.add_node("news", news)
    builder.add_node("sentiment", sentiment)
    builder.add_node("risk", risk)
    builder.add_node("summary", summary)

    builder.add_edge(START, "retriever")
    builder.add_edge(START, "tavily")
    builder.add_edge(START, "yfinance")

    builder.add_edge(
        ["retriever", "tavily", "yfinance"],
        "news",
    )
    builder.add_edge(
        ["retriever", "tavily", "yfinance"],
        "sentiment",
    )
    builder.add_edge(
        ["retriever", "tavily", "yfinance"],
        "risk",
    )
    builder.add_edge(
        ["news", "sentiment", "risk"],
        "summary",
    )

    builder.add_edge("summary", END)

    graph = builder.compile()
    graph.invoke({"completed": []})

    assert execution_order.count("summary") == 1
    assert execution_order[-1] == "summary"


def test_actual_market_graph_contains_expected_nodes_and_edges():
    graph = market_graph.graph

    graph_structure = graph.get_graph()

    expected_nodes = {
        "retriever",
        "tavily",
        "yfinance",
        "news_agent",
        "sentiment",
        "risk_agent",
        "summary",
        "memory_filter",
        "memory_compression",
        "memory_writer",
    }

    actual_nodes = set(graph_structure.nodes)

    assert expected_nodes.issubset(actual_nodes)

    actual_edges = {
        (edge.source, edge.target)
        for edge in graph_structure.edges
    }

    expected_edges = {
        ("__start__", "retriever"),
        ("__start__", "tavily"),
        ("__start__", "yfinance"),
        ("retriever", "news_agent"),
        ("tavily", "news_agent"),
        ("yfinance", "news_agent"),
        ("retriever", "sentiment"),
        ("tavily", "sentiment"),
        ("yfinance", "sentiment"),
        ("retriever", "risk_agent"),
        ("tavily", "risk_agent"),
        ("yfinance", "risk_agent"),
        ("news_agent", "summary"),
        ("sentiment", "summary"),
        ("risk_agent", "summary"),
        ("summary", "memory_filter"),
        ("memory_filter", "memory_compression"),
        ("memory_compression", "memory_writer"),
        ("memory_writer", "__end__"),
    }

    assert expected_edges.issubset(actual_edges)
