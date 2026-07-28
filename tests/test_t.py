# from tools.market_tools import search_tool

# query = "Latest Bitcoin ETF news and BTC outlook"

# result = search_tool.invoke(query)

# print(result)

import yfinance as yf

ticker = yf.Ticker("BTC")

print("Symbol:", ticker.info.get("symbol"))
print("Name:", ticker.info.get("longName"))
print("Exchange:", ticker.info.get("exchange"))
print("Type:", ticker.info.get("quoteType"))
print("Currency:", ticker.info.get("currency"))
print(ticker.fast_info)
print(ticker.history(period="5d"))