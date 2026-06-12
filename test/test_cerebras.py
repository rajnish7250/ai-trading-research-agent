# test_cerebras.py

from agents.llm_provider import get_llm

llm = get_llm("cerebras")

response = llm.invoke(
    "Explain Bitcoin ETF inflows in 2 sentences."
)

print(response.content)