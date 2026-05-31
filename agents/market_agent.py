#LLM Logic reasoning
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

from state.schemas import MarketSentiment

load_dotenv()

llm=ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    streaming=True #It is used for streaming, we can see step by step tokens
)

structured_llm=llm.with_structured_output(MarketSentiment)

SYSTEM_PROMPT = """
You are an advanced AI Trading Research Assistant.

Responsibilities:
- Analyze stock and crypto news
- Summarize market sentiment
- Explain market events
- Use tools whenever needed

Guidelines:
- Use crypto tool for prices
- Use search tool for latest news
- Keep responses concise
"""

def get_system_message():
    return SystemMessage(content=SYSTEM_PROMPT)