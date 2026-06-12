#shared memory/state between nodes
#super important in Langgraph

from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from state.schemas import MarketSentiment

class MarketState(TypedDict):
    # Conversation messages
    messages: Annotated[list, add_messages]
    
    # Structured Sentiment output
    sentiment: MarketSentiment
    #News analysis output
    news_summary: str
    #Risk analysis output
    risk_analysis: str
    
    #Retrieved RAG memory
    retrieved_context: str
    
    #Research Summary
    research_summary: str
    
    #Final LLM answer
    final_response: str
    #Memory Status
    memory_saved: bool
    
    #Memory Filtering
    memory_approved: bool
    