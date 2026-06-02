#LLM Logic reasoning
import os
from dotenv import load_dotenv


from agents.llm_provider import get_llm
from langchain_core.messages import SystemMessage

from state.schemas import MarketSentiment

load_dotenv()

llm=get_llm("groq")

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