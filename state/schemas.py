from typing import Literal
from pydantic import BaseModel, Field


class MarketSentiment(BaseModel):
    sentiment: Literal["Bullish", "Bearish", "Neutral"]
    confidence: Literal["Low", "Moderate", "High"]
    drivers: list[str] = Field(
        description="Top factors driving the market sentiment"
    )


class MarketRisk(BaseModel):
    risk_level: Literal["Low", "Medium", "High"]
    key_risks: list[str] = Field(
        description="Major risks and uncertainties"
    )
    watch_signal: str = Field(
        description="One important signal to monitor"
    )


class MarketNews(BaseModel):
    key_developments: list[str]
    etf_updates: list[str]
    regulatory_updates: list[str]
    market_data_summary: str


class ResearchRequest(BaseModel):
    query: str