from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
load_dotenv()

from memory.text_splitter import get_split_documents
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
    return vector_db

#Store documents
def store_documents():
    # Used for deleteing entire memory in vector_db
    # vector_db.delete_collection() 
    
    split_docs = get_split_documents()
    vector_db.add_documents(split_docs)
    print(f"Stored {len(split_docs)} documents")
    


if __name__ == "__main__":
    store_documents()
