from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from config import API_KEY
import logging
from utils import logging_config

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def verify_api_key(
    api_key: str = Security(api_key_header),
):
    """
    Verify incoming API Key.

    Raises:
        HTTPException(401) if invalid.
    """

    if api_key != API_KEY:
        logger.warning("Unauthorized API request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    return api_key