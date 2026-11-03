
import logging
import time

from state.market_state import MarketState
from memory.vector_store import get_vector_db
from config import MEMORY_SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)


def memory_filter_node(state: MarketState):
    start_time = time.perf_counter()

    logger.info("Memory filter node started")

    def log_rejection(reason: str, **details):
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        detail_message = " | ".join(
            f"{key}={value}" for key, value in details.items()
        )

        logger.info(
            "Memory filter rejected | reason=%s | %s"
            "duration_ms=%s",
            reason,
            detail_message + " | " if detail_message else "",
            duration_ms,
        )

    try:
        user_id = state.get("user_id")

        if not user_id:
            log_rejection("missing_user_id")
            return {
                "memory_approved": False,
                "memory_text": "",
            }

        report = state.get("research_summary")

        if report is None:
            log_rejection("missing_research_summary")
            return {
                "memory_approved": False,
                "memory_text": "",
            }

        # Convert structured ResearchReport into plain text.
        summary = f"""
Executive Summary:
{report.executive_summary}

Market Outlook:
{report.market_outlook}

Key Developments:
{chr(10).join("- " + item for item in report.key_developments)}

Sentiment:
{report.sentiment_summary}

Risk:
{report.risk_summary}

Watch Items:
{chr(10).join("- " + item for item in report.watch_items)}
""".strip()

        summary_length = len(summary)

        if not summary:
            log_rejection("empty_summary")
            return {
                "memory_approved": False,
                "memory_text": "",
            }

        if summary_length < 100:
            log_rejection(
                "summary_too_short",
                summary_length=summary_length,
            )
            return {
                "memory_approved": False,
                "memory_text": "",
            }

        vector_db = get_vector_db()

        results = vector_db.similarity_search_with_score(
            summary,
            k=1,
            filter={"user_id": user_id},
        )

        if results:
            _, score = results[0]

            if score < MEMORY_SIMILARITY_THRESHOLD:
                log_rejection(
                    "duplicate_memory",
                    similarity_score=score,
                )
                return {
                    "memory_approved": False,
                    "memory_text": "",
                }

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "Memory filter approved | summary_length=%s | "
            "duplicate_check_results=%s | duration_ms=%s",
            summary_length,
            len(results),
            duration_ms,
        )

        return {
            "memory_approved": True,
            "memory_text": summary,
        }

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "Memory filter failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise
