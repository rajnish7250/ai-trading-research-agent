#Creating Chatbot node
from state.market_state import MarketState
from tools.market_tools import (
    search_tool, 
    get_crypto_price
)

from agents.market_agent import(llm, get_system_message)

#Bind tools to LLM: LLM can't use tools by itself so need to bind. 
tools=[
    search_tool,
    get_crypto_price]

llm_with_tools=llm.bind_tools(tools)
def chatbot_node(state:MarketState):
    
    messages=state["messages"]
    response=llm_with_tools.invoke(
        [get_system_message()] + messages
    )
    
    return {
        "messages":[response]
    }