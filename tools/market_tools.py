'''tools/
External capabilities
Example:search,APIs,database,trading APIs'''
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool

load_dotenv()
_tavily =TavilySearchResults(max_results=5)

@tool
def search_market_news(query: str) -> str:
    """Search for the web for latest financial, stock and crypto market news"""
    result=_tavily.invoke({"query":query})
    return str(result)


search_tool= search_market_news
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


@tool
def get_stock_price(symbol: str) -> str:
    """
    Get latest stock or ETF price from Yahoo Finance.
    Indian NSE symbols must end with .NS(e.g. TATAGOLD.NS for Tata Gold ETF)
    US symbols examples: AAPL, GLD
    """

    ticker=yf.Ticker(symbol)
    data=ticker.history(period="1d")
    if data.empty:
        return f"No Price data found for {symbol}."

    latest_price = data["close"].iloc[-1]

    return f"latest price of {symbol} is {latest_price:.2f}"

stock_tool=get_stock_price