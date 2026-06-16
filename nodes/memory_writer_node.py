#memory_writer_node.py
from langchain_core.documents import Document
from state.market_state import MarketState
from memory.vector_store import get_vector_db

def memory_writer_node(state:MarketState):
    response= state.get("research_summary","")
    approved =state.get("memory_approved",False)
    print("\nMEMORY WRITER RECEIVED:\n")
    print(response)    
    if not response:
        return {"memory_saved": False}
    if not approved:
        print("\nMemory not approved, skipping save.\n")
        return {"memory_saved": False}
    doc=Document(
    page_content = response,
    metadata = {
        "source": "agent_generated",
        "type": "research_memory",
        "query": state["messages"][-1].content
    }
    )
    print("\nSaving research memory...\n")
    vector_db = get_vector_db()
    vector_db.add_documents([doc])
    print("\nResearch memory saved successfully\n")
    return {"memory_saved": True}