#retriever_node.py

from memory.vector_store import get_vector_db
from utils.asset_mapper import detect_symbol


def retriever_node(state):
    user_id = state.get("user_id")

    # Fail closed: never search shared memory without a user ID.
    if not user_id:
        return {"retrieved_context": ""}

    user_question = state["messages"][-1].content
    symbol = detect_symbol(user_question)

    search_query = f"{symbol} {user_question}" if symbol else user_question

    # Always restrict retrieval to the authenticated user.
    memory_filter = {"user_id": user_id}

    # If an asset is known, also restrict results to that asset.
    if symbol:
        memory_filter = {
            "$and": [
                {"user_id": user_id},
                {"asset": symbol},
            ]
        }

    vector_db = get_vector_db()
    retrieved_docs = vector_db.max_marginal_relevance_search(
        search_query,
        k=4,
        fetch_k=10,
        lambda_mult=0.5,
        filter=memory_filter,
    )

    context = "\n\n".join(doc.page_content for doc in retrieved_docs)

    return {"retrieved_context": context}
