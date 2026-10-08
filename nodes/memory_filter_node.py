from state.market_state import MarketState
from memory.vector_store import get_vector_db
from config import MEMORY_SIMILARITY_THRESHOLD


def memory_filter_node(state: MarketState):

    report = state.get("research_summary")

    print("\nMemory Filtering Running...\n")

    # Empty Check
    if report is None:
        print("Rejected: No research summary")
        return {
            "memory_approved": False,
            "memory_text": ""
        }

    # Convert structured ResearchReport into plain text
    summary = f"""
Executive Summary:
{report.executive_summary}

Market Outlook:
{report.market_outlook}

Key Developments:
{chr(10).join("- " + item for item in report.key_developments)}

Sentiment:
{report.sentiment_summary}

Risk:
{report.risk_summary}

Watch Items:
{chr(10).join("- " + item for item in report.watch_items)}
""".strip()

    summary_length = len(summary)

    # Empty Check
    if not summary:
        print("Rejected: Empty summary")
        return {
            "memory_approved": False,
            "memory_text": ""
        }

    # Length Check
    if summary_length < 100:
        print(f"Rejected: Summary too short ({summary_length} chars)")
        return {
            "memory_approved": False,
            "memory_text": ""
        }

    # -----------------------------------
    # Similarity Search (Observation Mode)
    # -----------------------------------

    vector_db = get_vector_db()

    results = vector_db.similarity_search_with_score(
        summary,
        k=1
    )

    if results:
        doc, score = results[0]

        print(f"\nSIMILARITY SCORE: {score}")

        if score < MEMORY_SIMILARITY_THRESHOLD:
            print("Rejected: Memory already exists")
            return {
                "memory_approved": False,
                "memory_text": ""
            }

    print("Approved for Storage")

    return {
        "memory_approved": True,
        "memory_text": summary
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