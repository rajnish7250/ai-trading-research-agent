import os
from dotenv import load_dotenv
MEMORY_SIMILARITY_THRESHOLD = 0.20
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
VALID_PROVIDERS = ["gemini", "groq", "cerebras", "mock"]

if LLM_PROVIDER not in VALID_PROVIDERS:
    raise ValueError(f"Invalid Provider: {LLM_PROVIDER}")

print(f"configured LLM Provider: {LLM_PROVIDER}")
