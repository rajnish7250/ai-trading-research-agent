#Creating Chatbot node
from state.market_state import MarketState
from langchain_core.messages import HumanMessage
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
    retrieved_context=state.get("retrieved_context", "")
    enhanced_message = HumanMessage(
        content = f"""
        Retrieved Research Context: 
        {retrieved_context}
        
        
        User Question: 
        
        {messages[-1].content}"""
    )

    response=llm_with_tools.invoke(
        [get_system_message(),
        enhanced_message]
    )
    
    return {
        "messages":[response]
    }