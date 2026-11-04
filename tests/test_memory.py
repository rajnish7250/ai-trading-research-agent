
"""
Manual ChromaDB inspection utility.

Run directly:
python tests/test_memory.py

This is intentionally not an automated pytest test.
"""

if __name__ == "__main__":
    from memory.vector_store import get_vector_db

    db = get_vector_db()
    collection = db._collection
    data = collection.get()

    print("TOTAL MEMORIES:", len(data["documents"]))

    for i, doc in enumerate(data["documents"], start=1):
        print(f"\nMemory #{i}")
        print("-" * 40)
        print(doc)
        print(data["metadatas"][i - 1])
