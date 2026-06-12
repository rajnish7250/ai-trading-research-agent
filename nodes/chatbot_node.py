#Creating Chatbot node
from state.market_state import MarketState
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.messages import AIMessage
from tools.market_tools import (search_tool, get_crypto_price, get_stock_price)
from utils.response_parser import extract_response_text
from agents.market_agent import(llm, get_system_message)

#Bind tools to LLM: LLM can't use tools by itself so need to bind. 
tools=[search_tool, get_crypto_price]

llm_with_tools=llm.bind_tools(tools, tool_choice="auto")
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

    # response=llm_with_tools.invoke(
    #     [get_system_message(),
    #     enhanced_message]
    # )
    #For Temporary testing without LLM
    response= AIMessage(
        content = """Bitcoin ETF inflows indicate increasing institutional interest, which is a positive signal for BTC. However, macroeconomic headwinds and regulatory uncertainties could limit near-term upside. Overall, cautiously optimistic sentiment with potential for volatility."""
    )
    parsed_response=extract_response_text(response)
    
    return {
        "messages":[response],
        "final_response": parsed_response
    }