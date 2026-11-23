# AI Trading Research Agent

Turn a plain-English market question into a structured report covering price movements, news, sentiment, and risks.

**[Watch the demo](https://www.youtube.com/watch?v=xM8v1rElqC8)** · **[Open the live app](https://ai-trading-research.mywire.org/)**

## What you can do

- Ask a research question about a stock or cryptocurrency.
- Explore price, news, sentiment, and risk in one report.
- Sign in to save reports and revisit them from **Saved Research**.

## Example question

> Analyze BTC-USD. What has changed in price recently, which news stories matter, and what risks should I watch?

## Built with

Streamlit and FastAPI serve the app. LangGraph coordinates the research workflow, SQLite stores accounts and saved reports, and ChromaDB stores research memory. The app runs on AWS EC2 with Docker and GitHub Actions.

Built by Rajnish Kumar.
