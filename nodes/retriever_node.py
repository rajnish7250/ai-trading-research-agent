#retriever_node.py
from memory.vector_store import get_vector_db
from utils.asset_mapper import detect_symbol

def retriever_node(state):
    user_question = state["messages"][-1].content
    symbol = detect_symbol(user_question)

    # bias the embedding toward the right asset, and filter to it if known
    search_query = f"{symbol} {user_question}" if symbol else user_question
    search_kwargs = {"k": 4, "fetch_k": 10, "lambda_mult":0.5}
    if symbol:
        search_kwargs["filter"] = {"asset": symbol}

    vector_db = get_vector_db()
    retrieved_docs = vector_db.max_marginal_relevance_search(search_query, **search_kwargs)

    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    return {"retrieved_context": context}