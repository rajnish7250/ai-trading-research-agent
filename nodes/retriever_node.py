#retriever_node.py
from memory.retriever import retriever

def retriever_node(state):
    
    #Get latest user message
    user_question = state["messages"][-1].content
    #Retrieve relevant research documents
    retrieved_docs= retriever.invoke(user_question)
    print("\nTotal Docs: ")
    print(len(retrieved_docs))
    
    # Convert docs into single string context
    context = "\n\n".join([
        doc.page_content for doc in retrieved_docs
    ])
    print("\nRETRIEVED CONTEXT:\n")
    print(context)
    
    #Return updated graph state
    return {
        "retrieved_context": context
    }
    
