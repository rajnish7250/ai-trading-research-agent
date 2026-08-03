import logging
from fastapi import FastAPI, Depends, HTTPException
from auth.api_key import verify_api_key

from utils import logging_config 
logger = logging.getLogger(__name__)

app=FastAPI()
logger.info("Starting AI Trading Research Agent")
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
def research(request: ResearchRequest, _: str = Depends(verify_api_key)):
    
    logger.info(f"Received research request: {request.query}")
    try:
        result = graph.invoke(
            {"messages": [HumanMessage(content= request.query)]},
            config={"configurable": {"thread_id": "user_1"}}
        )
        
        logger.info("Research completed successfully")   

        return { 
                # "response": result.get("final_response","No   Response generated")
                "price": result.get("market_price_data"),
                "news": result.get("news_summary"),
                "sentiment": result.get("sentiment"),
                "risk": result.get("risk_analysis"),
                "report": result.get("final_response")
                }
    except Exception:
        logger.exception("Research request failed")
        
        raise HTTPException(status_code=500, detail= "Internal Server Error")
        
        return {
            "error":"Internal Server Error"
        }
        
from datetime import datetime
@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }