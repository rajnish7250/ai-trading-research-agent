#memory_filter_node.py
from state.market_state import MarketState
from memory.vector_store import get_vector_db


def memory_filter_node(state: MarketState):

    summary = state.get("research_summary", "")
    summary_length = len(summary.strip())

    print("\nMemory Filtering Running...\n")

    # Empty Check
    if not summary.strip():

        print("Rejected: Empty summary")

        return {
            "memory_approved": False
        }

    # Length Check
    if summary_length < 100:

        print(
            f"Rejected: Summary too short ({summary_length}) chars"
        )

        return {
            "memory_approved": False
        }

    # -----------------------------------
    # Similarity Search (Observation Mode)
    # -----------------------------------

    vector_db = get_vector_db()

    results = vector_db.similarity_search_with_score(
        summary,
        k=1
    )
    print(type(results))
    
    if results:
        doc,score = results[0]

        print("\nMOST SIMILAR MEMORY:\n")

        print(doc.page_content)
        
        print(f"\nSIMILARITY SCORE: {score}")


    print(
        f"\nAccepted: Summary approved ({summary_length}) chars"
    )

    return {
        "memory_approved": True
    }