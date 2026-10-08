#llm_provider
from dotenv import load_dotenv
load_dotenv()

import logging
from utils import logging_config
logger=logging.getLogger(__name__)

from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_cerebras import ChatCerebras

from state.schemas import (
    MarketSentiment,
    MarketRisk,
    MarketNews,
    ResearchReport
)

class MockStructureLLM:

    def __init__(self, schema):
        self.schema = schema

    def with_structured_output(self, schema):
        return MockStructureLLM(schema)

    def invoke(self, messages):
        if self.schema == MarketNews:
            return MarketNews(
                key_developments=[
                    "Bitcoin continues to trade with elevated volatility",
                    "Institutional participation remains significant"
                ],
                etf_updates=[
                    "Bitcoin ETF activity remains an important market driver"
                ],
                regulatory_updates=[
                    "Regulatory developments continue to influence market sentiment"
                ],
                market_data_summary=(
                    "Bitcoin is trading around the latest observed market price "
                    "with elevated trading activity."
                )
            )        

        if self.schema == MarketSentiment:
            return MarketSentiment(
                sentiment="Bullish",
                confidence="High",
                drivers=[
                    "Positive market developments",
                    "Strong institutional activity",
                    "Favorable market conditions"
                ]
            )

        if self.schema == MarketRisk:
            return MarketRisk(
                risk_level="Medium",
                key_risks=[
                    "High market volatility",
                    "Regulatory uncertainty",
                    "Potential sentiment reversal"
                ],
                watch_signal="Monitor price volatility and market news"
            )
            
        if self.schema == ResearchReport:
            return ResearchReport(
                executive_summary=(
                    "Bitcoin is showing elevated volatility while "
                    "institutional participation remains significant."
                ),
                market_outlook=(
                    "The current outlook is mixed, with positive "
                    "institutional activity balanced against elevated risk."
                ),
                key_developments=[
                    "Bitcoin continues to trade with elevated volatility",
                    "Institutional participation remains significant"
                ],
                sentiment_summary=(
                    "Market sentiment is Bullish with High confidence, "
                    "supported by positive market developments and "
                    "institutional activity."
                ),
                risk_summary=(
                    "Risk is Medium due to high volatility, regulatory "
                    "uncertainty, and potential sentiment reversal."
                ),
                watch_items=[
                    "Bitcoin price volatility",
                    "ETF activity",
                    "Regulatory developments",
                    "Institutional activity"
                ]
            )

        raise ValueError(
            f"Unsupported structured output schema: {self.schema}"
        )
        
class MockLLM:

    def invoke(self, messages):

        return AIMessage(
            content=(
                "- Institutional participation remains significant.\n"
                "- Bitcoin ETF activity remains an important market driver.\n"
                "- Regulatory developments continue to influence the market.\n"
                "- Elevated market volatility remains a notable market condition."
            )
        )

    def bind_tools(self, tools, tool_choice="auto"):
        return self

    def with_structured_output(self, schema):
        return MockStructureLLM(schema)

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
            model="openai/gpt-oss-120b",
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

