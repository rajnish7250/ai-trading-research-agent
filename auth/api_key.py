from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from config import CURRENT_API_KEY, PREVIOUS_API_KEY
import logging
from utils import logging_config

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)

# Build the set of valid API keys once during application startup
VALID_API_KEYS = {CURRENT_API_KEY}

if PREVIOUS_API_KEY:
    VALID_API_KEYS.add(PREVIOUS_API_KEY)


def verify_api_key(
    api_key: str = Security(api_key_header),
):
    """
    Verify incoming API Key.

    Raises:
        HTTPException(401) if the API Key invalid.
    """

    if api_key not in VALID_API_KEYS:
        logger.warning("Unauthorized API Request")
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Invalid API Key",)

    return api_key