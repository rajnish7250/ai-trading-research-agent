from pydantic import BaseModel
class MarketSentiment(BaseModel):
    asset:str
    sentiment:str
    confidence:str
    summary:str
    
class ResearchRequest(BaseModel):
    query: str