from langchain_core.messages import HumanMessage

from graphs.market_graph import graph

from utils.response_parser import extract_response_text

# --------------------------------------------
# USER INPUT
# --------------------------------------------
# user_input = "What is the current BTC outlook?"
# user_input = " What happened after Bitcoin ETF approval?"
user_input = input("Enter your market research query: ")
print(f"USER INPUT:\n{user_input}\n")

# --------------------------------------------
# GRAPH EXECUTION
# --------------------------------------------
result = graph.invoke(
    {
        "messages": [
            HumanMessage(content=user_input)
        ]
    },
    config={
        "configurable":{
            "thread_id": "user_1"
        }
    }
)

print("\nFINAL AI RESPONSE:\n")

response_text= extract_response_text(result["final_response"])
print(response_text)
