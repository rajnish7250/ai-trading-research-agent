from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import uuid

from utils.logging_config import request_id_context

import logging
from fastapi import (
    Request,
    FastAPI,
    Depends,
    HTTPException,
    Query,
    status,
)

from config import AUTH_ENABLED

from utils import logging_config 
logger = logging.getLogger(__name__)

from auth.schemas import Token
from fastapi.security import OAuth2PasswordRequestForm
from auth.service import authenticate_user 
from auth.jwt_handler import create_access_token 
from auth.dependencies import get_current_user

app=FastAPI()

class RequestIDMiddleware:
    """Attach a unique request ID to every HTTP request."""

    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex
        token = request_id_context.set(request_id)

        start_time = time.perf_counter()
        status_code = 500

        async def send_with_request_id(message):
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]

                headers = list(message.get("headers", []))
                headers.append(
                    (b"x-request-id", request_id.encode("ascii"))
                )

                message["headers"] = headers

            await send(message)

        try:
            self.logger.info(
                "HTTP request started | method=%s | path=%s",
                scope["method"],
                scope["path"],
            )

            await self.app(scope, receive, send_with_request_id)

        except Exception:
            self.logger.exception("Unhandled HTTP request exception")
            raise

        finally:
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            self.logger.info(
                "HTTP request completed | status_code=%s | duration_ms=%s",
                status_code,
                duration_ms,
            )

            request_id_context.reset(token)


app.add_middleware(RequestIDMiddleware)


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger.info("Starting AI Trading Research Agent")
@app.get("/")

def home():
    return {
        "message":"AI Trading Research Agent Running"
    }
    
    

@app.post("/login", response_model=Token, include_in_schema=AUTH_ENABLED)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    logger.info("Login attempt")

    # The user enters their email in Swagger's username field.
    user = authenticate_user(
        form_data.username,
        form_data.password,
    )

    if not user:
        logger.warning("Login failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    logger.info("Login successful")

    access_token = create_access_token(
        {"sub": user["email"]}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )

    
from state.schemas import ResearchRequest
from langchain_core.messages import HumanMessage
from graphs.market_graph import graph
from services.research_service import perform_research
from services.research_history_store import (
    save_research,
    get_research_history,
)

@app.post("/research")
@limiter.limit("5/minute")
def research(
    request: Request,
    body: ResearchRequest,
    current_user: dict = Depends(get_current_user),
):
    logger.info("Received research request")

    try:
        result = perform_research(
            query=body.query,
            user_id=current_user["email"],
        )

        response_data = {
            "price": result.get("market_price_data"),
            "news": result.get("news_summary"),
            "sentiment": result.get("sentiment"),
            "risk": result.get("risk_analysis"),
            "report": result.get("final_response"),
        }

        save_research(
            user_id=current_user["email"],
            query=body.query,
            result=response_data,
        )

        return response_data

    except Exception:
        logger.exception("Research request failed")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        )
@app.get("/research/history")
def research_history(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    return get_research_history(
        user_id=current_user["email"],
        limit=limit,
    )

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