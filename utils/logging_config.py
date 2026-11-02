
import logging
import time
from contextvars import ContextVar

# Store the request ID for the current execution context.
request_id_context = ContextVar("request_id", default="-")

# Use local server time in log timestamps.
logging.Formatter.converter = time.localtime


class RequestContextFilter(logging.Filter):
    """Attach the current request ID to every log record."""

    def filter(self, record):
        record.request_id = request_id_context.get()
        return True


# Configure application logging.
logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | request_id=%(request_id)s | %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Attach the filter to root logging handlers.
root_logger = logging.getLogger()

for handler in root_logger.handlers:
    if not any(
        isinstance(existing_filter, RequestContextFilter)
        for existing_filter in handler.filters
    ):
        handler.addFilter(RequestContextFilter())

# Reduce noise from third-party libraries.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
