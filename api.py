from fastapi import FastAPI
app=FastAPI()

@app.get("/")

def home():
    return {
        "message":"AI Trading Research Agent Running"
    }
    
from state.schemas import ResearchRequest
# @app.post("/research")
# def research(request: ResearchRequest):
#     return { "query": request.query}

from langchain_core.messages import HumanMessage
from graphs.market_graph import graph

@app.post("/research")
def research(request: ResearchRequest):
    try:
        result = graph.invoke(
            {"messages": [HumanMessage(content= request.query)]},
            config={"configurable": {"thread_id": "user_1"}}
        )   

        return { 
                # "response": result.get("final_response","No   Response generated")
                "price": result.get("market_price_data"),
                "news": result.get("news_summary"),
                "sentiment": result.get("sentiment"),
                "risk": result.get("risk_analysis"),
                "report": result.get("final_response")
                }
    except Exception as e:
        return {
            "error": str(e)
        }