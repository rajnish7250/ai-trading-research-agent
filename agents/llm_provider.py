from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

def get_llm(provider="gemini"):
    if provider=="gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )
    elif provider=="groq":
        return ChatGroq(
            # model="llama-3.3-70b-versatile",
            model="llama-3.1-8b-instant",
            temperature=0,
            streaming=True 
            )
    else:
        raise ValueError(f"Provider {provider} not supported")

