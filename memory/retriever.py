#retriever.py
from memory.vector_store import get_vector_db
vector_db=get_vector_db()
retriever = vector_db.as_retriever(
    # search_type="mmr",#MMR avoids repetitive retrieval
    search_type="similarity",
    search_kwargs= {
        "k":2,
        # "filter": {"ticker":"BTC"} #Used for more making comparison directly to the ticker. For more specific search
    }
)
def retrieve_research(query):
    
    results= retriever.invoke(query)
    print("\nRetrieved Documents:\n")
    for result in results:
        print("Content: ")
        print(result.page_content)
        
        print("METADATA: ")
        print(result.metadata)
        print("\n")
        
if __name__=="__main__":
    query= input("Enter Research Query: ")
    retrieve_research(query)
    # "What is current BTC outlook"

        
        
        
