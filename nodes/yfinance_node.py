#yfinance_node.py
from state.market_state import MarketState
from tools.market_tools import (
    get_crypto_price,
    get_stock_price
)

from utils.asset_mapper import detect_symbol


def yfinance_mode(state: MarketState):

    user_question = state["messages"][-1].content

    symbol = detect_symbol(user_question)

    print(f"\nDETECTED SYMBOL: {symbol}")

    if not symbol:
        return {
            "market_price_data":
            "No supported asset detected."
        }

    if symbol.endswith("-USD"):
        result = get_crypto_price.invoke(symbol)

    else:
        result = get_stock_price.invoke(symbol)

    print("\n===== PRICE DATA =====\n")
    print(result)

    return {
        "market_price_data": str(result)
    }