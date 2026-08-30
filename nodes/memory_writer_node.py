#memory_writer_node.py
from langchain_core.documents import Document
from state.market_state import MarketState
from memory.vector_store import get_vector_db
from memory.text_splitter import split_summary
from utils.asset_mapper import detect_symbol

def memory_writer_node(state:MarketState):
    response= state.get("memory_summary","")
    approved =state.get("memory_approved",False)
    print("\nMEMORY WRITER RECEIVED:\n")
    print(response)    
    if not response:
        return {"memory_saved": False}
    if not approved:
        print("\nMemory not approved, skipping save.\n")
        return {"memory_saved": False}
    
    metadata = {
        "source": "agent_generated",
        "type": "research_memory",
        "query": state["messages"][-1].content,
        "asset": detect_symbol(state["messages"][-1].content) or "unknown",
    }
    chunks = split_summary(response, metadata)
    print(f"\nSaving research memory as {len(chunks)} chunk(s)...\n")
    vector_db = get_vector_db()
    vector_db.add_documents(chunks) 
     
    print("\nResearch memory saved successfully\n")
    return {"memory_saved": True}