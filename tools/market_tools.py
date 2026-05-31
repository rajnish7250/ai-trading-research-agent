'''tools/
External capabilities
Example:search,APIs,database,trading APIs'''
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool

load_dotenv()
search_tool=TavilySearchResults(max_results=5)

import yfinance as yf
@tool
def get_crypto_price(symbol: str) -> str:
    """ 
    Get latest cryptocurrency price.
    Example symbols:
    BTC-USD
    ETH-USD"""
    
    ticker=yf.Ticker(symbol)
    data=ticker.history(period="1d")
    
    if data.empty:
        return "No price data found."
    
    latest_price=data["Close"].iloc[-1]
    
    return f"Latest price of {symbol} is ${latest_price:.2f}"
