#retriever.py
import logging
from utils import logging_config

logger = logging.getLogger(__name__)
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
    logger.info("Searching Historical Memories")
    results= retriever.invoke(query)
    print("\nRetrieved Documents:\n")        
    logger.info(f"Retrieved {len(results)} documents ")
        
if __name__=="__main__":
    query= input("Enter Research Query: ")
    retrieve_research(query)
    # "What is current BTC outlook"

        

        
        
        
