#retriever_node.py
from memory.retriever import retriever
def retriever_node(state):
    user_question = state["messages"][-1].content
    retrieved_docs= retriever.invoke(user_question)
    # Convert docs into single string context
    context = "\n\n".join([
        doc.page_content for doc in retrieved_docs
        ])
    
    #Storing metadata also
    # context = [
    #     {
    #         "content": doc.page_content,
    #         "metadata": doc.metadata
    #     }
    #     for doc in retrieved_docs
    #     ]
    return {
        "retrieved_context": context
    }
    
