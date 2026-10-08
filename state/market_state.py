#market_state.py

from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from state.schemas import (
    MarketSentiment,
    MarketRisk,
    MarketNews,
    ResearchReport
)

class MarketState(TypedDict):
    # Conversation messages
    messages: Annotated[list, add_messages]
    # Structured Sentiment output
    
    # For tavily
    market_news: str
    market_price_data: str
    
    #News analysis output
    news_summary: MarketNews | None
    # sentiment:
    sentiment: MarketSentiment | None
    #Risk analysis output
    risk_analysis: MarketRisk | None
    #Retrieved RAG memory
    retrieved_context: str

    #Research Summary
    research_summary: ResearchReport | None 
    
    memory_text: str
    #Compressed, durable-only memory
    memory_summary: str 
    
    
    #Final response
    final_response: str   
    #Memory Status
    memory_saved: bool
    #Memory Filtering
    memory_approved: bool
    