#llm_provider
from dotenv import load_dotenv
load_dotenv()

import logging
from utils import logging_config
logger=logging.get_logger(__name__)

from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_cerebras import ChatCerebras

from state.schemas import MarketSentiment
class MockStructureLLM:
    def invoke(self, messages):
        return MarketSentiment(
            sentiment="Bullish",
            confidence=0.85,
            reasoning="Mock sentiment"
        )
        
class MockLLM:
    def invoke(self, messages):
        return AIMessage(
            content= "Mock Response"
            )
    def bind_tools(self, tools, tool_choice= "auto"):
        return self
    
    def with_structured_output(self, schema):
        return MockStructureLLM()

#Other LLM providers can be added here with same interface: OpenRouter, 
def get_llm(provider="gemini"):
    if provider=="gemini":
        logger.info("Initializing Gemini LLM")
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )
    elif provider=="groq":
        logger.info("Initializing Groq LLM")
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            # model="llama-3.1-8b-instant",
            temperature=0,
            streaming= False 
            )
    
    elif provider=="cerebras":
        logger.info("Initializing Cerebras LLM")
        return ChatCerebras(
            model="gpt-oss-120b",
            temperature=0,
            streaming=False
        )
        
    elif provider=="mock":
        logger.info("Initializing Mock LLM")
        return MockLLM()
    
    else:
        logger.error(f"Unsupported LLM Provider: {provider}")
        raise ValueError(f"Provider {provider} not Supported")

