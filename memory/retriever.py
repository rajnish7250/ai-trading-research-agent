#Import vector_db from vector_store.py
from memory.vector_store import get_vector_db
# from vector_store import vector_db
vector_db=get_vector_db()
#Create retriever object
retriever = vector_db.as_retriever(
    #Configure retrieval settings
    # search_type="mmr",#MMR avoids repetitive retrieval
    search_type="similarity",
    search_kwargs= {
        #Number of documents to retreive
        "k":2,
        # "filter": {"ticker":"BTC"} #Used for more making comparison directly to the ticker. For more specific search
    }
)

#Function to retrieve research documents
def retrieve_research(query):
    
    #retrieve semantically relevant documents
    results= retriever.invoke(query)
    
    #Print Separator
    print("\nRetrieved Documents:\n")
    #Loop through retrieved documents
    for result in results:
        #Print main content
        print("Content: ")
        print(result.page_content)
        
        #Print Metadata
        print("METADATA: ")
        print(result.metadata)
        print("\n")
        
#Run only if file executed directly
if __name__=="__main__":
    #Example query
    retrieve_research(
        "What was previous BTC outlook"
    )
        
