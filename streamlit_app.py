
import os

import requests
import streamlit as st


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

REQUEST_TIMEOUT = 180

st.set_page_config(
    page_title="AI Trading Research Agent",
    page_icon="📈",
    layout="wide",
)


def api_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def load_history():
    """Load saved research belonging to the authenticated user."""
    response = requests.get(
        f"{API_BASE_URL}/research/history",
        headers=api_headers(),
        params={"limit": 50},
        timeout=15,
    )

    if response.status_code == 401:
        st.session_state.token = None
        st.session_state.email = None
        st.session_state.history = []
        st.error("Your session has expired. Please log in again.")
        st.rerun()

    response.raise_for_status()
    st.session_state.history = response.json()


def login(email, password):
    """Authenticate against FastAPI and store the returned JWT."""
    response = requests.post(
        f"{API_BASE_URL}/login",
        json={"email": email, "password": password},
        timeout=15,
    )

    if response.status_code == 401:
        st.error("Invalid email or password.")
        return False

    response.raise_for_status()
    st.session_state.token = response.json()["access_token"]
    st.session_state.email = email
    st.session_state.history = []
    return True


def logout():
    st.session_state.token = None
    st.session_state.email = None
    st.session_state.history = []
    st.rerun()


# Initialize session state.
if "token" not in st.session_state:
    st.session_state.token = None

if "email" not in st.session_state:
    st.session_state.email = None

if "history" not in st.session_state:
    st.session_state.history = []

if "selected_report" not in st.session_state:
    st.session_state.selected_report = None


st.title("📈 AI Trading Research Agent")
st.caption(
    "Multi-agent market research powered by LangGraph, "
    "RAG, market data, news, sentiment and risk analysis."
)


# Login screen.
if not st.session_state.token:
    st.subheader("Sign in")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:
        if not email.strip() or not password:
            st.warning("Enter both your email and password.")
        else:
            try:
                if login(email.strip(), password):
                    st.rerun()
            except requests.RequestException:
                st.error(
                    "Cannot connect to the API. "
                    "Check that FastAPI is running and API_BASE_URL is correct."
                )

    st.info("Log in to research markets and access your saved reports.")
    st.stop()


# Authenticated application.
with st.sidebar:
    st.subheader("Account")
    st.write(st.session_state.email)

    if st.button("Refresh history", use_container_width=True):
        try:
            load_history()
            st.rerun()
        except requests.RequestException:
            st.error("Could not load research history.")

    if st.button("Log out", use_container_width=True):
        logout()

    st.divider()
    st.subheader("Saved research")

    history = st.session_state.history

    if not history:
        st.caption("No saved reports loaded yet.")
    else:
        for item in history:
            label = (
                f"{item['query'][:45]} "
                f"· {item['created_at'][:10]}"
            )

            if st.button(
                label,
                key=f"history_{item['id']}",
                use_container_width=True,
            ):
                st.session_state.selected_report = item
                st.rerun()


# Load history after login or when the page session is restored.
if not st.session_state.history:
    try:
        load_history()
    except requests.RequestException:
        st.warning("Could not load saved reports from the API.")


selected = st.session_state.selected_report

if selected:
    st.subheader("Saved research report")
    st.caption(f"Query: {selected['query']}")

    if st.button("Close saved report"):
        st.session_state.selected_report = None
        st.rerun()

    st.json(selected["result"])
    st.caption(f"Saved at: {selected['created_at']}")

else:
    st.subheader("New market research")

    with st.form("research_form"):
        query = st.text_area(
            "Research query",
            placeholder=(
                "Example: Analyze BTC-USD market sentiment, "
                "recent news and key risks."
            ),
            height=100,
        )

        submitted = st.form_submit_button(
            "Run research",
            use_container_width=True,
        )

    if submitted:
        if not query.strip():
            st.warning("Enter a research question first.")
        else:
            try:
                with st.spinner(
                    "Researching market data, news, sentiment and risk..."
                ):
                    response = requests.post(
                        f"{API_BASE_URL}/research",
                        headers=api_headers(),
                        json={"query": query.strip()},
                        timeout=REQUEST_TIMEOUT,
                    )

                    response.raise_for_status()
                    result = response.json()

                st.success("Research completed.")

                st.subheader("Research results")

                for section in (
                    "price",
                    "news",
                    "sentiment",
                    "risk",
                    "report",
                ):
                    with st.expander(
                        section.replace("_", " ").title(),
                        expanded=(section == "report"),
                    ):
                        value = result.get(section)

                        if isinstance(value, (dict, list)):
                            st.json(value)
                        elif value is not None:
                            st.write(value)
                        else:
                            st.caption("No data returned.")

                # Refresh saved reports from the backend.
                load_history()

            except requests.HTTPError as exc:
                status_code = (
                    exc.response.status_code
                    if exc.response is not None
                    else "unknown"
                )
                st.error(
                    f"The API returned HTTP {status_code}. "
                    "Check the API logs for details."
                )

            except requests.Timeout:
                st.error(
                    "The research request timed out. "
                    "Check whether the backend is still processing it."
                )

            except requests.RequestException:
                st.error(
                    "Could not reach the API. "
                    "Verify that FastAPI is running."
                )


st.divider()
st.caption(
    "Streamlit UI · FastAPI · LangGraph · RAG · ChromaDB · SQLite"
)
