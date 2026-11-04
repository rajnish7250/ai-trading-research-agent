
from typing import TypedDict
from types import SimpleNamespace
from unittest.mock import MagicMock

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from graphs import market_graph
from state.schemas import (
    MarketNews,
    MarketSentiment,
    MarketRisk,
    ResearchReport,
)


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
        ("yfinance", "risk_agent"),
        ("retriever", "risk_agent"),
        ("tavily", "risk_agent"),
        ("news_agent", "summary"),
        ("sentiment", "summary"),
        ("risk_agent", "summary"),
        ("summary", "memory_filter"),
        ("memory_filter", "memory_compression"),
        ("memory_compression", "memory_writer"),
        ("memory_writer", "__end__"),
    }

    assert expected_edges.issubset(actual_edges)


def test_actual_market_graph_executes_end_to_end(monkeypatch):
    import nodes.retriever_node as retriever_module
    import nodes.tavily_node as tavily_module
    import nodes.yfinance_node as yfinance_module
    import nodes.news_node as news_module
    import nodes.sentiment_node as sentiment_module
    import nodes.risk_node as risk_module
    import nodes.summary_node as summary_module
    import nodes.memory_filter_node as filter_module
    import nodes.memory_compression_node as compression_module
    import nodes.memory_writer_node as writer_module

    # Fake vector database: no real ChromaDB access.
    fake_db = MagicMock()
    fake_db.max_marginal_relevance_search.return_value = []
    fake_db.similarity_search_with_score.return_value = []
    fake_db.add_documents.return_value = None

    monkeypatch.setattr(
        retriever_module,
        "get_vector_db",
        lambda: fake_db,
    )
    monkeypatch.setattr(
        filter_module,
        "get_vector_db",
        lambda: fake_db,
    )
    monkeypatch.setattr(
        writer_module,
        "get_vector_db",
        lambda: fake_db,
    )

    # Fake Tavily search.
    fake_search = MagicMock()
    fake_search.invoke.return_value = [
        {"title": "Bitcoin institutional adoption update"}
    ]

    monkeypatch.setattr(
        tavily_module,
        "search_tool",
        fake_search,
    )

    # Fake YFinance price response.
    fake_price = MagicMock()
    fake_price.invoke.return_value = "BTC price: $90,000"

    monkeypatch.setattr(
        yfinance_module,
        "get_crypto_price",
        fake_price,
    )

    # Fake structured news response.
    monkeypatch.setattr(
        news_module,
        "structured_news_llm",
        MagicMock(
            invoke=lambda prompt: MarketNews(
                key_developments=[
                    "Institutional adoption update"
                ],
                etf_updates=["ETF market update"],
                regulatory_updates=["Regulatory update"],
                market_data_summary="Bitcoin market data available",
            )
        ),
    )

    # Fake structured sentiment response.
    monkeypatch.setattr(
        sentiment_module,
        "structured_sentiment_llm",
        MagicMock(
            invoke=lambda prompt: MarketSentiment(
                sentiment="Bullish",
                confidence="Moderate",
                drivers=["Institutional adoption"],
            )
        ),
    )

    # Fake structured risk response.
    monkeypatch.setattr(
        risk_module,
        "structured_risk_llm",
        MagicMock(
            invoke=lambda prompt: MarketRisk(
                risk_level="Medium",
                key_risks=["Market volatility"],
                watch_signal="ETF inflows",
            )
        ),
    )

    # Fake structured research report.
    monkeypatch.setattr(
        summary_module,
        "structured_summary_llm",
        MagicMock(
            invoke=lambda prompt: ResearchReport(
                executive_summary=(
                    "Bitcoin shows positive institutional developments."
                ),
                market_outlook="Cautiously positive",
                key_developments=[
                    "Institutional adoption update"
                ],
                sentiment_summary="Moderately bullish",
                risk_summary="Market volatility remains a concern",
                watch_items=["ETF inflows"],
            )
        ),
    )

    # Fake memory compression response.
    monkeypatch.setattr(
        compression_module,
        "compression_llm",
        MagicMock(
            invoke=lambda prompt: SimpleNamespace(
                content=(
                    "- Institutional adoption developments "
                    "remain relevant to Bitcoin."
                )
            )
        ),
    )

    # Fake document splitting to avoid real storage dependencies.
    monkeypatch.setattr(
        writer_module,
        "split_summary",
        lambda text, metadata: [
            SimpleNamespace(
                page_content=text,
                metadata=metadata,
            )
        ],
    )

    # Execute the actual compiled production graph.
    result = market_graph.graph.invoke(
        {
            "messages": [
                HumanMessage(content="Research BTC-USD")
            ],
            "user_id": "integration_test_user",
        },
        config={
            "configurable": {
                "thread_id": "integration_test_end_to_end"
            }
        },
    )

    # Verify analysis pipeline.
    assert result["news_summary"].key_developments
    assert result["sentiment"].sentiment == "Bullish"
    assert result["risk_analysis"].risk_level == "Medium"

    # Verify final report.
    assert result["research_summary"].executive_summary
    assert "Market Research Report" in result["final_response"]

    # Verify memory lifecycle.
    assert result["memory_approved"] is True
    assert result["memory_summary"]
    assert result["memory_saved"] is True

    # Verify memory was written to the fake database.
    fake_db.add_documents.assert_called_once()
