from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import logging
from fastapi import FastAPI, Depends, HTTPException, status
from auth.api_key import verify_api_key

from utils import logging_config 
logger = logging.getLogger(__name__)

from auth.schemas import (LoginRequest, Token)
from auth.service import authenticate_user 
from auth.jwt_handler import create_access_token 

app=FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger.info("Starting AI Trading Research Agent")
@app.get("/")

def home():
    return {
        "message":"AI Trading Research Agent Running"
    }
    
    
@app.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest):
    logger.info("Login attempt")
    user = authenticate_user(body.email, body.password)
    
    if not user:
        logger.warning("Login failed")
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid email or password",
        )
        
                
    logger.info("Login successful")
    
    access_token = create_access_token(
        { "sub": user["email"],}
    )
    return Token(access_token = access_token, token_type="bearer")
    
from state.schemas import ResearchRequest
from langchain_core.messages import HumanMessage
from graphs.market_graph import graph
from services.research_service import perform_research

@app.post("/research")
@limiter.limit("1/minute")
def research(request: Request, body: ResearchRequest, _: str = Depends(verify_api_key)):
    logger.info(f"Received research request: {body.query}")
    try:
        result = perform_research(body.query)
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
    
from fastapi import Depends
from auth.dependencies import get_current_user 
from services.research_service import perform_research 

        
from datetime import datetime
@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }