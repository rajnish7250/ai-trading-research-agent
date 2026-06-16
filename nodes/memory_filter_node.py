#memory_filter_node.py
from state.market_state import MarketState
from memory.vector_store import get_vector_db
from config import MEMORY_SIMILARITY_THRESHOLD
def memory_filter_node(state: MarketState):

    summary = state.get("research_summary", "")
    summary_length = len(summary.strip())
    print("\nMemory Filtering Running...\n")
    # REJECT_TERMS = [
    #     "bullish",
    #     "bearish",
    #     "neutral",
    #     "buy",
    #     "sell",
    #     "strong buy",
    #     "strong sell",
    #     "confidence",
    #     "high confidence",
    #     "low confidence",
    #     "market outlook",
    #     "risk level",
    #     "positive sentiment",
    #     "negative sentiment",
    # ]
    # summary_lower=summary.lower()
    # if any(term in summary_lower for term in REJECT_TERMS):
    #     return {
    #         "approved":False,
    #         "reason": "Contains temporary market opinions"
    #     }
    # Empty Check
    if not summary.strip():
        print("Rejected: Empty summary")
        return {"memory_approved": False}
    # Length Check
    if summary_length < 100:
        print(f"Rejected: Summary too short ({summary_length}) chars")
        return {"memory_approved": False}
    # -----------------------------------
    # Similarity Search (Observation Mode)
    # -----------------------------------
    vector_db = get_vector_db()
    results = vector_db.similarity_search_with_score(
        summary,
        k=1
    )  
    if results:
        doc,score = results[0]
        if score < MEMORY_SIMILARITY_THRESHOLD:
            print(f"\nSIMILARITY SCORE: {score}")
            print("Rejected: Memory already exists")
            return {"memory_approved": False}     
        
    print("Approved for Storage")
    return {
        "memory_approved": True
    }
    
if __name__ == "__main__":
    vector_db = get_vector_db()

    test_text = """
    Bitcoin ETF assets declined significantly.
    """

    results = vector_db.similarity_search_with_score(
        test_text,
        k=3
    )

    print("\nSEARCH RESULTS:\n")

    for i, (doc, score) in enumerate(results, start=1):
        print(f"\nResult {i}")
        print("-" * 50)
        print(f"Score: {score}")
        print(doc.page_content[:300])