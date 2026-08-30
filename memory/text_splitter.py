from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

def split_summary(text: str, metadata: dict):
    """Splits a research summary into chunks, each carrying the same metadata."""
    return splitter.create_documents([text], metadatas=[metadata])