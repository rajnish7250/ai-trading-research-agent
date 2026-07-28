##Method 1: Similarity Search Test
# from memory.vector_store import get_vector_db

# db=get_vector_db()
# results= db.similarity_search(
#     "Bitcoin ETF inflows",
#     k=5
# )

# print(f"found{len(results)} documents \n")

# for i, doc in enumerate(results):
#     print(f"Document {i+1}:")
#     print("-"*50)
#     print(doc.page_content)
#     print(doc.metadata)
#     print()
    
###Method 2: Show entire Collection
from memory.vector_store import get_vector_db
db = get_vector_db()
collection = db._collection
data = collection.get()
print("TOTAL MEMORIES:", len(data["documents"]))
for i, doc in enumerate(data["documents"], start=1):
    print("\n-------------------")
    print(f"Memory #{i}")
    print(doc)
    print(data["metadatas"][i-1])
    
###Method 3: Check Chroma MetaData(Useful for debugging duplicates)
# from memory.vector_store import get_vector_db

# db = get_vector_db()

# collection = db._collection

# data = collection.get()

# print(data.keys())
