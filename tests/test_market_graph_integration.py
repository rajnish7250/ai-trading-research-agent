
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
        ("yfinance", "sentiment"),
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


import logging
import pytest


def test_actual_market_graph_propagates_tavily_failure(monkeypatch, caplog):
    import nodes.retriever_node as retriever_module
    import nodes.tavily_node as tavily_module
    import nodes.yfinance_node as yfinance_module

    # Prevent access to the real ChromaDB.
    fake_db = MagicMock()
    fake_db.max_marginal_relevance_search.return_value = []

    monkeypatch.setattr(
        retriever_module,
        "get_vector_db",
        lambda: fake_db,
    )

    # Simulate a Tavily API failure.
    fake_search = MagicMock()
    fake_search.invoke.side_effect = RuntimeError(
        "Tavily service unavailable"
    )

    monkeypatch.setattr(
        tavily_module,
        "search_tool",
        fake_search,
    )

    # Prevent a real YFinance API call.
    fake_price = MagicMock()
    fake_price.invoke.return_value = "BTC price: $90,000"

    monkeypatch.setattr(
        yfinance_module,
        "get_crypto_price",
        fake_price,
    )

    caplog.set_level(
        logging.ERROR,
        logger="nodes.tavily_node",
    )

    # Execute the actual compiled production graph.
    with pytest.raises(
        RuntimeError,
        match="Tavily service unavailable",
    ):
        market_graph.graph.invoke(
            {
                "messages": [
                    HumanMessage(content="Research BTC-USD")
                ],
                "user_id": "integration_test_failure_user",
            },
            config={
                "configurable": {
                    "thread_id": "integration_test_tavily_failure"
                }
            },
        )

    # Verify Tavily was called.
    fake_search.invoke.assert_called_once()

    # Verify the node recorded its failure.
    assert "Tavily node failed" in caplog.text
    assert "error_type=RuntimeError" in caplog.text
    
    

def test_actual_market_graph_rejects_duplicate_memory(monkeypatch):
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

    # Fake database.
    fake_db = MagicMock()

    fake_db.max_marginal_relevance_search.return_value = []

    # Similarity score below the configured threshold means duplicate.
    fake_db.similarity_search_with_score.return_value = [
        (MagicMock(), 0.1)
    ]

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

    # Fake Tavily.
    fake_search = MagicMock()
    fake_search.invoke.return_value = [
        {"title": "Bitcoin institutional adoption update"}
    ]

    monkeypatch.setattr(
        tavily_module,
        "search_tool",
        fake_search,
    )

    # Fake YFinance.
    fake_price = MagicMock()
    fake_price.invoke.return_value = "BTC price: $90,000"

    monkeypatch.setattr(
        yfinance_module,
        "get_crypto_price",
        fake_price,
    )

    # Fake analysis agents.
    monkeypatch.setattr(
        news_module,
        "structured_news_llm",
        MagicMock(
            invoke=lambda prompt: MarketNews(
                key_developments=["Institutional adoption update"],
                etf_updates=["ETF market update"],
                regulatory_updates=["Regulatory update"],
                market_data_summary="Bitcoin market data available",
            )
        ),
    )

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

    monkeypatch.setattr(
        summary_module,
        "structured_summary_llm",
        MagicMock(
            invoke=lambda prompt: ResearchReport(
                executive_summary=(
                    "Bitcoin shows positive institutional developments."
                ),
                market_outlook="Cautiously positive",
                key_developments=["Institutional adoption update"],
                sentiment_summary="Moderately bullish",
                risk_summary="Market volatility remains a concern",
                watch_items=["ETF inflows"],
            )
        ),
    )

    # Track whether compression executes.
    compression_mock = MagicMock()

    compression_mock.invoke.return_value = SimpleNamespace(
        content="- Institutional adoption developments."
    )

    monkeypatch.setattr(
        compression_module,
        "compression_llm",
        compression_mock,
    )

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

    # Execute actual compiled production graph.
    result = market_graph.graph.invoke(
        {
            "messages": [
                HumanMessage(content="Research BTC-USD")
            ],
            "user_id": "integration_test_duplicate_user",
        },
        config={
            "configurable": {
                "thread_id": "integration_test_duplicate_memory"
            }
        },
    )

    # Research should still complete successfully.
    assert result["research_summary"] is not None
    assert result["final_response"]

    # Duplicate memory must be rejected.
    assert result["memory_approved"] is False
    assert result["memory_text"] == ""

    # Compression must skip.
    assert result["memory_summary"] == ""
    compression_mock.invoke.assert_not_called()

    # Writer must not persist anything.
    assert result["memory_saved"] is False
    fake_db.add_documents.assert_not_called()
    

def test_actual_market_graph_rejects_short_memory(
    monkeypatch,
    caplog,
):
    import logging

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

    # Fake vector database: prevent real ChromaDB access.
    fake_db = MagicMock()
    fake_db.max_marginal_relevance_search.return_value = []
    fake_db.similarity_search_with_score.return_value = []

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
        {"title": "Bitcoin market update"}
    ]

    monkeypatch.setattr(
        tavily_module,
        "search_tool",
        fake_search,
    )

    # Fake YFinance.
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
                key_developments=["Bitcoin update"],
                etf_updates=[],
                regulatory_updates=[],
                market_data_summary="Market data available",
            )
        ),
    )

    # Fake sentiment response.
    monkeypatch.setattr(
        sentiment_module,
        "structured_sentiment_llm",
        MagicMock(
            invoke=lambda prompt: MarketSentiment(
                sentiment="Bullish",
                confidence="Moderate",
                drivers=["Market activity"],
            )
        ),
    )

    # Fake risk response.
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

    # Return a deliberately short research report.
    monkeypatch.setattr(
        summary_module,
        "structured_summary_llm",
        MagicMock(
            invoke=lambda prompt: ResearchReport(
                executive_summary="BTC",
                market_outlook="",
                key_developments=[],
                sentiment_summary="",
                risk_summary="",
                watch_items=[],
            )
        ),
    )

    # Track whether memory compression executes.
    compression_mock = MagicMock()

    monkeypatch.setattr(
        compression_module,
        "compression_llm",
        compression_mock,
    )

    # Track whether memory document splitting executes.
    split_summary_mock = MagicMock()

    monkeypatch.setattr(
        writer_module,
        "split_summary",
        split_summary_mock,
    )

    # Capture memory-filter logs.
    caplog.set_level(
        logging.INFO,
        logger="nodes.memory_filter_node",
    )

    # Execute the actual compiled production graph.
    result = market_graph.graph.invoke(
        {
            "messages": [
                HumanMessage(content="Research BTC-USD")
            ],
            "user_id": "integration_test_short_memory_user",
        },
        config={
            "configurable": {
                "thread_id": "integration_test_short_memory_rejection"
            }
        },
    )

    # Research report generation must succeed.
    assert result["research_summary"] is not None
    assert result["final_response"]
    assert "Market Research Report" in result["final_response"]

    # Short memory must be rejected.
    assert result["memory_approved"] is False
    assert result["memory_text"] == ""

    # Verify the short-summary rejection reason was logged.
    assert "reason=summary_too_short" in caplog.text
    assert "summary_length=95" in caplog.text

    # Duplicate detection must not execute.
    fake_db.similarity_search_with_score.assert_not_called()

    # Memory compression must skip execution.
    assert result["memory_summary"] == ""
    compression_mock.invoke.assert_not_called()

    # Memory writer must skip execution.
    assert result["memory_saved"] is False
    split_summary_mock.assert_not_called()
    fake_db.add_documents.assert_not_called()
    
    
def test_langgraph_parallel_nodes_receive_request_id():
    from langgraph.graph import StateGraph, START, END
    from utils.logging_config import request_id_context
    from typing import TypedDict

    class TestState(TypedDict, total=False):
        completed: list[str]

    captured_request_ids = {}

    def make_node(name):
        def node(state):
            captured_request_ids[name] = request_id_context.get()
            return {}
        return node

    builder = StateGraph(TestState)

    builder.add_node("news_agent", make_node("news_agent"))
    builder.add_node("sentiment", make_node("sentiment"))
    builder.add_node("risk_agent", make_node("risk_agent"))

    builder.add_edge(START, "news_agent")
    builder.add_edge(START, "sentiment")
    builder.add_edge(START, "risk_agent")

    builder.add_edge(
        ["news_agent", "sentiment", "risk_agent"],
        END,
    )

    graph = builder.compile()

    request_id = "test-request-123"
    token = request_id_context.set(request_id)

    try:
        graph.invoke({"completed": []})
    finally:
        request_id_context.reset(token)

    assert captured_request_ids == {
        "news_agent": request_id,
        "sentiment": request_id,
        "risk_agent": request_id,
    }


