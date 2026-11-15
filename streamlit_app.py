
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
    page_icon="ðŸ“ˆ",
    layout="wide",
)


def api_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }

def expire_session():
    """Clear authentication state when the JWT expires."""
    st.session_state.token = None
    st.session_state.email = None
    st.session_state.history = []
    st.session_state.history_loaded = False
    st.session_state.selected_report = None

    st.error("Your session has expired. Please log in again.")
    st.rerun()


def load_history():
    """Load saved research belonging to the authenticated user."""
    response = requests.get(
        f"{API_BASE_URL}/research/history",
        headers=api_headers(),
        params={"limit": 50},
        timeout=15,
    )

    if response.status_code == 401:
        expire_session()

    response.raise_for_status()
    st.session_state.history = response.json()
    st.session_state.history_loaded = True


def login(email, password):
    """Authenticate against FastAPI and store the returned JWT."""
    response = requests.post(
        f"{API_BASE_URL}/login",
        data={"username": email, "password": password},
        timeout=15,
    )

    if response.status_code == 401:
        st.error("Invalid email or password.")
        return False

    response.raise_for_status()
    st.session_state.token = response.json()["access_token"]
    st.session_state.email = email
    st.session_state.history = []
    st.session_state.history_loaded = False
    return True


def logout():
    st.session_state.token = None
    st.session_state.email = None
    st.session_state.history = []
    st.session_state.history_loaded = False
    st.session_state.selected_report = None
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

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False


st.title("ðŸ“ˆ AI Trading Research Agent")
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
            except requests.HTTPError as exc:
                status_code = (
                    exc.response.status_code
                    if exc.response is not None
                    else None
                )

                if status_code == 403:
                    st.error("Access denied. Please contact the administrator.")
                elif status_code == 422:
                    st.error("Invalid login request. Please check your input.")
                elif status_code == 429:
                    st.error("Too many login attempts. Please wait and try again.")
                elif status_code and status_code >= 500:
                    st.error("Login service is temporarily unavailable.")
                else:
                    st.error(f"Login failed. HTTP {status_code or 'unknown'}.")

            except requests.Timeout:
                st.error("Login request timed out. Please try again.")

            except requests.ConnectionError:
                st.error("Cannot connect to the API. Check whether FastAPI is running.")

            except requests.RequestException:
                st.error("An unexpected error occurred during login.")

    st.info("Log in to research markets and access your saved reports.")
    st.stop()


# Authenticated application.
with st.sidebar:
    st.subheader("Account")
    st.write(st.session_state.email)

    if st.button("Refresh history", use_container_width=True):
        try:
            load_history()
            st.success("Research history refreshed.")
            st.rerun()

        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else None
            )

            if status_code == 401:
                expire_session()
            elif status_code == 403:
                st.error("You don't have permission to view this history.")
            elif status_code and status_code >= 500:
                st.error("Server error while loading history. Try again later.")
            else:
                st.error(f"Could not load history. HTTP {status_code or 'unknown'}.")

        except requests.Timeout:
            st.error("History request timed out. Please try again.")

        except requests.RequestException:
            st.error("Cannot connect to the API.")

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
                f"Â· {item['created_at'][:10]}"
            )

            if st.button(
                label,
                key=f"history_{item['id']}",
                use_container_width=True,
            ):
                st.session_state.selected_report = item
                st.rerun()


# Load history after login or when the page session is restored.
if not st.session_state.history_loaded:
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
                    if response.status_code == 401:
                        expire_session()

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
                    else None
                )
                if status_code == 401:
                    expire_session()

                elif status_code == 403:
                    st.error("You don't have permission to perform this action. ")
                elif status_code == 422:
                    st.error("The research request contains invalid data. Please check your input.")
                elif status_code == 429:
                    st.error("API rate limit reached. Please wait before trying again.")
                elif status_code and status_code >= 500:
                    st.error("The server encountered an error. Please try again later.")
                else:
                    st.error(f"API request failed. HTTP status: {status_code or 'unknown'}")
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
    "Streamlit UI Â· FastAPI Â· LangGraph Â· RAG Â· ChromaDB Â· SQLite"
)
