import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# AI Configuration
# =========================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")

VALID_PROVIDERS = [
    "gemini",
    "groq",
    "cerebras",
    "mock",
]

if LLM_PROVIDER not in VALID_PROVIDERS:
    raise ValueError(f"Invalid Provider: {LLM_PROVIDER}")

# =========================
# Memory Configuration
# =========================

MEMORY_SIMILARITY_THRESHOLD = 0.20

# =========================
# API Key Authentication
# =========================

CURRENT_API_KEY = os.getenv("CURRENT_API_KEY")
PREVIOUS_API_KEY = os.getenv("PREVIOUS_API_KEY")

if not CURRENT_API_KEY:
    raise ValueError(
        "CURRENT_API_KEY environment variable is not configured."
    )

# =========================
# JWT Authentication
# =========================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY environment variable is not configured."
    )