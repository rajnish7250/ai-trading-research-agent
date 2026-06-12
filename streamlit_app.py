import warnings 
warnings.filterwarnings("ignore", message=".*__path__.*")
import uuid

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from graphs.market_graph import graph

from utils.response_parser import extract_response_text


def _get_assistant_reply(result: dict) -> str:

    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage):
            return extract_response_text(message)
        return "No Response Generated"


st.set_page_config(
    page_title="AI Trading Agent",
    page_icon="📈",
    layout="wide",
)

st.title("AI Trading Research Assistant")
st.caption("Ask about crypto, stocks, market news, or your indexed research.")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_context" not in st.session_state:
    st.session_state.last_context = ""

with st.sidebar:
    st.header("Session")
    st.text(f"Thread: {st.session_state.thread_id[:8]}...")

    if st.button("Clear chat", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.session_state.last_context = ""
        st.rerun()

    st.divider()
    st.header("Capabilities")
    st.markdown(
        """
        - **RAG** — searches your Chroma research index
        - **Tavily** — latest market news
        - **yfinance** — live crypto prices (e.g. `BTC-USD`)
        """
    )

    if st.session_state.last_context:
        with st.expander("Last retrieved context"):
            st.text(st.session_state.last_context)

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("e.g. What is the current BTC outlook?")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching and analyzing..."):
            try:
                result = graph.invoke(
                    {"messages": [HumanMessage(content=prompt)]},
                    config={
                        "configurable": {
                            "thread_id": st.session_state.thread_id,
                        }
                    },
                )
                reply = _get_assistant_reply(result)
                context = result.get("retrieved_context", "")
                if context:
                    st.session_state.last_context = context
            except Exception as exc:
                reply = (
                    f"Something went wrong: {exc}\n\n"
                    "Check your `.env` keys (GROQ, TAVILY) and run "
                    "`python memory/vector_store.py` to index research docs."
                )

        st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
