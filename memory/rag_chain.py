from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from retriever import retriever

##Step 2: Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

prompt = ChatPromptTemplate.from_template(
    """
You are an AI Trading Research Assistant.

Use the retrieved market research context below
to answer the user's question.

Carefully analyze the context and generate a concise
market insight based on the retrieved research.

If relevant information exists, summarize it clearly.

Retrieved Context:
{context}

User Question:
{question}

Answer:
"""
)

##Step 3: Main Rag Function
def ask_research_agent(question):
    #Retrieve relevant documents
    retrieved_docs= retriever.invoke(question)
    
    # convert documents into string
    context="\n\n".join(
        [doc.page_content for doc in retrieved_docs]
    )
    
    #Create final Prompt
    final_prompt = prompt.invoke({
        "context": context,
        "question": question
    })
    
    print("\nRETRIEVED DOCS: \n")
    print(context)
    
    #Generate LLM response
    response = llm. invoke(final_prompt)
    
    #Print response
    print('\nAI Response: \n')
    print(response.content)
    
#Step 4: Run example

if __name__=="__main__":
    ask_research_agent(
        "What was previous BTC outlook"
    )
