import os
from dotenv import load_dotenv

load_dotenv()

MEMORY_SIMILARITY_THRESHOLD = 0.20

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")

CURRENT_API_KEY = os.getenv("CURRENT_API_KEY")
PREVIOUS_API_KEY = os.getenv("PREVIOUS_API_KEY")

VALID_PROVIDERS = ["gemini", "groq", "cerebras", "mock"]

if LLM_PROVIDER not in VALID_PROVIDERS:
    raise ValueError(f"Invalid Provider: {LLM_PROVIDER}")

if not CURRENT_API_KEY:
    raise ValueError("CURRENT_API_KEY environment variable is not configured.")
