# streamlit_app.py

import warnings
warnings.filterwarnings("ignore", message=".*__path__.*")

import uuid
import streamlit as st
from langchain_core.messages import HumanMessage

from graphs.market_graph import graph


# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="AI Trading Research Agent",
    page_icon="📈",
    layout="wide",
)

# ---------------------------
# Session State
# ---------------------------
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_context" not in st.session_state:
    st.session_state.last_context = ""

# ---------------------------
# Header
# ---------------------------
st.title("AI Trading Research Agent")

st.markdown("""
Research markets using:

✅ Live Price Data (Yahoo Finance)

✅ Real-Time News (Tavily)

✅ AI Sentiment Analysis

✅ Risk Assessment

✅ Research Memory (ChromaDB)
""")

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:

    st.header("Session")

    st.text(
        f"Thread: {st.session_state.thread_id[:8]}..."
    )

    if st.button(
        "Clear Chat",
        use_container_width=True
    ):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.session_state.last_context = ""
        st.rerun()

    st.divider()

    st.header("Capabilities")

    st.markdown("""
- **RAG** — Search research memory
- **Tavily** — Latest market news
- **Yahoo Finance** — Live market prices
- **Sentiment Analysis**
- **Risk Assessment**
""")

# ---------------------------
# Chat History
# ---------------------------
for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------
# User Input
# ---------------------------
prompt = st.chat_input(
    "Ask about BTC, stocks, market outlook, news..."
)

# ---------------------------
# Run Agent
# ---------------------------
if prompt:

    # User Message
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Message
    with st.chat_message("assistant"):

        with st.spinner(
            "Fetching market data, news, sentiment and risk analysis..."
        ):

            try:

                result = graph.invoke(
                    {
                        "messages": [
                            HumanMessage(content=prompt)
                        ]
                    },
                    config={
                        "configurable": {
                            "thread_id":
                            st.session_state.thread_id
                        }
                    },
                )

                reply = result.get(
                    "final_response",
                    "No response generated."
                )

                context = result.get(
                    "retrieved_context",
                    ""
                )

                if context:
                    st.session_state.last_context = context

            except Exception as exc:

                reply = f"""
❌ Error

{str(exc)}

Possible fixes:

- Check Gemini API key
- Check Tavily API key
- Verify ChromaDB initialization
- Verify internet connection
"""

        st.markdown(reply)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

# ---------------------------
# Footer
# ---------------------------
st.divider()

st.caption(
    "Built with LangGraph • Gemini • Tavily • ChromaDB • Streamlit"
)