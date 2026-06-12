#Workflows orchestration
#Langgraph lives here
#Market_graph should only know which node exist and how nodes are connected. 
from langgraph.graph import (StateGraph,START,END)

from langgraph.prebuilt import (ToolNode, tools_condition)
from langgraph.checkpoint.memory import MemorySaver

# Graph State
from state.market_state import MarketState
# Nodes
from nodes.chatbot_node import chatbot_node
from nodes.retriever_node import retriever_node
from nodes.sentiment_node import sentiment_node
from nodes.news_node import news_agent_node
from nodes.risk_node import risk_agent_node
from nodes.memory_writer_node import memory_writer_node
from nodes.summary_node import summary_node
from nodes.memory_filter_node import memory_filter_node
# Tools
from tools.market_tools import (search_tool, get_crypto_price, get_stock_price)
# ---------------------------------------------------
# TOOLS
# ---------------------------------------------------
tools = [search_tool, get_crypto_price, get_stock_price]
tool_node = ToolNode(tools=tools)
# ---------------------------------------------------
# GRAPH BUILDER
# ---------------------------------------------------
graph_builder = StateGraph(MarketState)

# ---------------------------------------------------
# ADD NODES
# ---------------------------------------------------
graph_builder.add_node(
    "retriever",
    retriever_node
)

graph_builder.add_node(
    "chatbot",
    chatbot_node
)

graph_builder.add_node(
    "tools",
    tool_node
)

graph_builder.add_node(
    "sentiment",
    sentiment_node
)

graph_builder.add_node(
    "news_agent",
    news_agent_node
)

graph_builder.add_node(
    "risk_agent",
    risk_agent_node
)

graph_builder.add_node(
    "memory_writer",
    memory_writer_node
)

graph_builder.add_node(
    "summary",
    summary_node
)
graph_builder.add_node(
    "memory_filter",
    memory_filter_node
)
# ---------------------------------------------------
# GRAPH FLOW
# ---------------------------------------------------

graph_builder.add_edge(
    START,
    "retriever"
)
graph_builder.add_edge(
    "retriever",
    "news_agent"
)

graph_builder.add_edge(
    "news_agent",
    "sentiment"
)

graph_builder.add_edge(
    "sentiment",
    "risk_agent"
)
graph_builder.add_edge(
    "risk_agent",
    "summary"
)
graph_builder.add_edge(
    "summary",
    "memory_filter"
)
graph_builder.add_edge(
    "memory_filter",
    "memory_writer"
)

graph_builder.add_edge(
    "memory_writer",
    END
)

# ---------------------------------------------------
# MEMORY
# ---------------------------------------------------
memory = MemorySaver()

# ---------------------------------------------------
# COMPILE GRAPH
# ---------------------------------------------------
graph = graph_builder.compile(
    checkpointer=memory
)

# ---------------------------------------------------
# VISUALIZATION (run this file directly to preview the graph)
# ---------------------------------------------------

if __name__ == "__main__":
    print(graph.get_graph().draw_ascii())

    from IPython.display import Image, display

    display(Image(graph.get_graph().draw_mermaid_png()))