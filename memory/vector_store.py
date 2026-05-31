from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()

from memory.text_splitter import get_split_documents

#Step1- Creating Embedding Model
#This model converts normal text into AI underastandable (vectors/number)

def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )


def get_vector_db():
    embedding_model=get_embedding_model()
    return Chroma(
        collection_name="market_research",
        embedding_function = embedding_model,
        persist_directory="./chroma_db"
    )
#Used for deleteing entire memory in vector_db
# vector_db.delete_collection()

#Store documents
def store_documents():
    vector_db= get_vector_db()
    split_docs = get_split_documents()
    vector_db.add_documents(split_docs)

if __name__ == "__main__":
    store_documents()




    