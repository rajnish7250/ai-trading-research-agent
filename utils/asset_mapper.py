ASSET_MAP = {
    # Crypto
    "btc": "BTC-USD",
    "bitcoin": "BTC-USD",
    "eth": "ETH-USD",
    "ethereum": "ETH-USD",

    # Commodities
    "gold": "GC=F",
    "silver": "SI=F",
    "oil": "CL=F",

    # Stocks
    "apple": "AAPL",
    "tesla": "TSLA",
    "microsoft": "MSFT",
    "nvidia": "NVDA",

    # Indexes
    "nasdaq": "^IXIC",
    "sp500": "^GSPC",
    "s&p500": "^GSPC",
    "nifty": "^NSEI",
    "sensex": "^BSESN",
}


def detect_symbol(query: str):

    query = query.lower()

    for keyword, symbol in ASSET_MAP.items():
        if keyword in query:
            return symbol

    return None