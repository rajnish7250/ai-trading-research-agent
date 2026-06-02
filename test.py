from agents.llm_provider import get_llm

llm = get_llm()

response = llm.invoke("What is Bitcoin?")

print(response.content)