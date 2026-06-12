from dotenv import load_dotenv
load_dotenv()

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
        print("Using MOCK LLM")
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
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )
    elif provider=="groq":
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            # model="llama-3.1-8b-instant",
            temperature=0,
            streaming= False 
            )
    
    elif provider=="cerebras":
        
        return ChatCerebras(
            model="gpt-oss-120b",
            temperature=0,
            streaming=False
        )
        
    elif provider=="mock":
        return MockLLM()
    
    else:
        raise ValueError(f"Provider {provider} not supported")

