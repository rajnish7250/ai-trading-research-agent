from datetime import datetime
import sys
import os

os.makedirs("logs", exist_ok=True)

filename = f"logs/run_{datetime.now():%Y%m%d_%H%M%S}.txt"

log_file = open(filename, "w", encoding="utf-8")


class Logger:
    def __init__(self, *files):
        self.files = files

    def write(self, text):
        for f in self.files:
            f.write(text)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()


sys.stdout = Logger(sys.stdout, log_file)
sys.stderr = Logger(sys.stderr, log_file)

print(f"Logging to: {filename}")

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

print("\nFINAL RESULT:\nIgnoring as long \n")
# print(result)

print("\nRESULT KEYS:\n")
print(result.keys())

print("\nFINAL AI RESPONSE:\n")

response_text= extract_response_text(result["final_response"])
print(response_text)

try:
    # existing code
    ...
finally:
    log_file.close()
