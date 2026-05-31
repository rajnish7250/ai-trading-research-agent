from langchain_core.messages import HumanMessage

from graphs.market_graph import graph


# --------------------------------------------
# USER INPUT
# --------------------------------------------

user_input = "What is the current BTC outlook?"
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


# --------------------------------------------
# FINAL RESPONSE
# --------------------------------------------

print("\nFINAL AI RESPONSE:\n")

print(
    result["messages"][-1].content
)