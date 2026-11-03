#yfinance_node.py

import logging
import time

from state.market_state import MarketState
from tools.market_tools import (
    get_crypto_price,
    get_stock_price,
)
from utils.asset_mapper import detect_symbol

logger = logging.getLogger(__name__)


def yfinance_mode(state: MarketState):
    start_time = time.perf_counter()

    logger.info("YFinance node started")

    try:
        user_question = state["messages"][-1].content
        symbol = detect_symbol(user_question)

        if not symbol:
            logger.warning(
                "YFinance node skipped | reason=no_supported_asset_detected"
            )

            return {
                "market_price_data": "No supported asset detected."
            }

        if symbol.endswith("-USD"):
            asset_type = "crypto"
            result = get_crypto_price.invoke(symbol)
        else:
            asset_type = "stock"
            result = get_stock_price.invoke(symbol)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.info(
            "YFinance node completed | asset_type=%s | "
            "duration_ms=%s",
            asset_type,
            duration_ms,
        )

        return {
            "market_price_data": str(result)
        }

    except Exception as exc:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.error(
            "YFinance node failed | duration_ms=%s | error_type=%s",
            duration_ms,
            type(exc).__name__,
        )

        raise
