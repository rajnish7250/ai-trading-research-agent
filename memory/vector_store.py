#vector_store.py
# vector_store.py
#         │
#         ├── Embeddings
#         │
#         └── ChromaDB
#                 │
#      ┌──────────┼──────────┐
#      │          │          │
# Retriever  MemoryFilter  MemoryWriter

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
load_dotenv()
# =====================================================
# LOAD ONCE AT APPLICATION STARTUP
# =====================================================
print("Loading Embedding Model...")
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)
print("Initializing ChromaDB...")
vector_db = Chroma(
    collection_name="market_research",
    embedding_function=embedding_model,
    persist_directory="./chroma_db"
)
# =====================================================
# GETTERS
# =====================================================
def get_embedding_model():
    return embedding_model
def get_vector_db():
    #This below two command is for deploying on streamlit
    import os 
    os.makedirs("chroma_db", exist_ok = True)
    
    return vector_db

from langchain_core.documents import Document 
if __name__ == "__main__":
    vector_db.delete_collection()
    vector_db = Chroma(
        collection_name="market_research",
        embedding_function=embedding_model,
        persist_directory="./chroma_db"
    )
    vector_db.add_documents([
        Document(
            page_content="Bitcoin ETF assets declined significantly."
        )
    ])

    print("Test memory inserted")
    