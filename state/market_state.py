#market_state.py

from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from state.schemas import MarketSentiment

class MarketState(TypedDict):
    # Conversation messages
    messages: Annotated[list, add_messages]
    # Structured Sentiment output
    
    # For tavily
    market_news: str
    market_price_data: str
    
    #News analysis output
    news_summary: str
    # sentiment:
    sentiment: str
    #Risk analysis output
    risk_analysis: str
    #Retrieved RAG memory
    retrieved_context: str

    #Research Summary
    research_summary: str 
    
    
    #Final response
    final_response: str   
    #Memory Status
    memory_saved: bool
    #Memory Filtering
    memory_approved: bool
    