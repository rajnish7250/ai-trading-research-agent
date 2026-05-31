from langchain_groq import ChatGroq
news_llm= ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

sentiment_llm=ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

risk_llm=ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


NEWS_AGENT_PROMPT = """
You are a Market News Research Agent.

Responsibilities:
- Find latest market-moving news
- Focus on factual developments
- Summarize important events clearly
- Mention macroeconomic impact
"""


SENTIMENT_AGENT_PROMPT = """
You are a Market Sentiment Analysis Agent.

Responsibilities:
- Analyze market psychology
- Determine bullish/bearish sentiment
- Identify fear/greed signals
- Estimate confidence level
"""


RISK_AGENT_PROMPT = """
You are a Trading Risk Analysis Agent.

Responsibilities:
- Identify downside risks
- Mention volatility concerns
- Analyze uncertainty
- Highlight market dangers
"""