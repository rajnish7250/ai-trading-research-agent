"""Streamlit workspace for the AI Trading Research Agent."""

import os
import re
from html import escape

import requests
import streamlit as st

from ui_theme import apply_theme
from auth_ui import (
    validate_registration,
    register_account,
    verify_account,
    resend_verification,
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 180

st.set_page_config(
    page_title="AI Trading Research Agent | Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()


# ─────────────────────────────────────────────────────────────────────────────
# API and session helpers — same endpoints and request formats as before.
# ─────────────────────────────────────────────────────────────────────────────

def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def clear_user_session():
    st.session_state.token = None
    st.session_state.email = None
    st.session_state.history = []
    st.session_state.history_loaded = False
    st.session_state.selected_report = None
    st.session_state.last_result = None
    st.session_state.last_query = ""
    st.session_state.auth_view = "login"
    st.session_state.pending_verify_token = None
    st.session_state.pending_reset_token = None
    st.session_state.show_settings = False


def expire_session():
    """Clear authentication state when the JWT expires."""
    clear_user_session()
    st.session_state.flash_message = "Your session expired. Please sign in again."
    st.rerun()


def load_history():
    """Fetch saved reports for the signed-in user."""
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
    """Authenticate against FastAPI and save its access token."""
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
    st.session_state.selected_report = None
    st.session_state.last_result = None
    st.session_state.last_query = ""
    return True


def logout():
    clear_user_session()
    st.rerun()


def status_code_from(exc):
    return exc.response.status_code if exc.response is not None else None


def display_login_error(exc):
    code = status_code_from(exc)
    if code == 403:
        st.error("Access denied. Please contact the administrator.")
    elif code == 422:
        st.error("Invalid login request. Please check your input.")
    elif code == 429:
        st.error("Too many login attempts. Please wait and try again.")
    elif code and code >= 500:
        st.error("Login service is temporarily unavailable.")
    else:
        st.error(f"Login failed. HTTP {code or 'unknown'}.")


def display_research_error(exc):
    code = status_code_from(exc)
    if code == 401:
        expire_session()
    elif code == 403:
        st.error("You don't have permission to perform this action.")
    elif code == 422:
        st.error("The research request contains invalid data. Please check your input.")
    elif code == 429:
        st.error("API rate limit reached. Please wait before trying again.")
    elif code and code >= 500:
        st.error("The server encountered an error. Please try again later.")
    else:
        st.error(f"API request failed. HTTP status: {code or 'unknown'}.")


def display_history_error(exc):
    code = status_code_from(exc)
    if code == 401:
        expire_session()
    elif code == 403:
        st.error("You don't have permission to view this history.")
    elif code and code >= 500:
        st.error("Server error while loading history. Try again later.")
    else:
        st.error(f"Could not load history. HTTP {code or 'unknown'}.")


# ─────────────────────────────────────────────────────────────────────────────
# UI helpers — only presentation, no changes to research data or APIs.
# ─────────────────────────────────────────────────────────────────────────────

def pretty_label(value):
    """Convert API keys such as 'market_sentiment' into friendly labels."""
    label = str(value).replace("_", " ").replace("-", " ").strip()
    return re.sub(r"\s+", " ", label).title() or "Detail"


def render_detail(value, depth=0):
    """Present unpredictable nested agent output without hiding its content."""
    if value is None:
        st.caption("No data returned for this section.")
    elif isinstance(value, dict):
        if not value:
            st.caption("No data returned for this section.")
            return
        if depth >= 3:
            st.json(value)
            return
        for key, child in value.items():
            label = pretty_label(key)
            if isinstance(child, (dict, list)):
                st.markdown(f"**{label}**")
                render_detail(child, depth + 1)
            else:
                left, right = st.columns([1, 2.3])
                with left:
                    st.caption(label)
                with right:
                    if child is None or child == "":
                        st.caption("Not available")
                    else:
                        st.write(child)
    elif isinstance(value, list):
        if not value:
            st.caption("No items returned.")
            return
        for index, item in enumerate(value[:12], 1):
            if isinstance(item, dict):
                title = item.get("title") or item.get("headline") or item.get("name")
                if title is not None:
                    st.markdown(f"**{index}. {escape(str(title))}**")
                    remaining = {key: val for key, val in item.items()
                                 if key not in ("title", "headline", "name")}
                    render_detail(remaining, depth + 1)
                else:
                    st.markdown(f"**Item {index}**")
                    render_detail(item, depth + 1)
            else:
                st.write(item)
            if index < min(len(value), 12):
                st.divider()
        if len(value) > 12:
            with st.expander(f"View {len(value) - 12} more items"):
                st.json(value[12:])
    elif isinstance(value, str):
        st.write(value)
    else:
        st.write(value)


def render_report(result, heading="Research intelligence"):
    """Render new and saved reports in the same readable interface."""
    st.markdown('<div class="tr-section-label">YOUR ANALYSIS</div>', unsafe_allow_html=True)
    st.markdown(f"### {heading}")

    if not isinstance(result, dict):
        render_detail(result)
        return

    sections = [
        ("report", "📋 Report"),
        ("price", "📈 Price"),
        ("news", "📰 News"),
        ("sentiment", "🧠 Sentiment"),
        ("risk", "🛡️ Risk"),
    ]
    present = [(key, label) for key, label in sections if key in result]
    extra = {key: val for key, val in result.items() if key not in dict(sections)}

    if not present and not extra:
        st.info("The research service returned an empty report.")
        return

    tab_labels = [label for _, label in present]
    if extra:
        tab_labels.append("🔎 Other data")
    tab_labels.append("{} Raw JSON".format("🗂️"))

    tabs = st.tabs(tab_labels)
    for index, (key, _) in enumerate(present):
        with tabs[index]:
            st.markdown(f"#### {pretty_label(key)} analysis")
            render_detail(result[key])
    if extra:
        with tabs[len(present)]:
            render_detail(extra)
    with tabs[-1]:
        st.caption("Complete unmodified API response for transparency and debugging.")
        st.json(result)


def display_topbar():
    st.markdown(
        '<div class="tr-topbar">'
        '<span class="tr-logo">◈</span>'
        '<span class="tr-brand">AI TRADING <span class="tr-brand-accent">RESEARCH</span></span>'
        '<span class="tr-topbar-tag">AI RESEARCH AGENT</span>'
        '</div>',
        unsafe_allow_html=True,
    )


for name, default in {
    "token": None,
    "email": None,
    "history": [],
    "history_loaded": False,
    "selected_report": None,
    "last_result": None,
    "last_query": "",
    "flash_message": None,
    "auth_view": "login",
    "pending_verify_token": None,
    "pending_reset_token": None,
    "show_settings": False,
}.items():
    if name not in st.session_state:
        st.session_state[name] = default


def auth_request_error(exc):
    """Display safe, friendly authentication errors."""
    if isinstance(exc, requests.Timeout):
        st.error("The request timed out. Please try again.")
    elif isinstance(exc, requests.ConnectionError):
        st.error("Cannot connect to FastAPI. Check that it is running.")
    elif isinstance(exc, requests.HTTPError):
        code = status_code_from(exc)
        if code == 429:
            st.warning("Too many requests. Please wait before trying again.")
        elif code == 400:
            st.error("The request could not be completed. Check your details or verification link.")
        elif code == 422:
            st.error("Please check the information you entered.")
        elif code and code >= 500:
            st.error("The authentication service is temporarily unavailable.")
        else:
            st.error("The request could not be completed.")
    else:
        st.error("Something went wrong. Please try again.")


def show_registration():
    st.subheader("Create your account")
    st.caption("Register to access your AI research workspace.")

    with st.form("registration_form"):
        full_name = st.text_input("Full name")
        email = st.text_input("Email address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input(
            "Confirm password", type="password"
        )
        submitted = st.form_submit_button(
            "Create account", type="primary", use_container_width=True
        )

    if submitted:
        error = validate_registration(
            full_name, email, password, confirm_password
        )
        if error:
            st.warning(error)
        else:
            try:
                message = register_account(
                    API_BASE_URL, full_name, email, password
                )
                st.success(message)
                st.info(
                    "Check your inbox and spam folder. "
                    "If no email arrives, use Resend verification."
                )
            except requests.RequestException as exc:
                auth_request_error(exc)

    if st.button("Already have an account? Sign in"):
        st.session_state.auth_view = "login"
        st.rerun()

    if st.button("Resend verification email"):
        st.session_state.auth_view = "resend"
        st.rerun()


def show_resend_verification():
    st.subheader("Resend verification email")
    st.caption("Enter the email address used during registration.")

    with st.form("resend_form"):
        email = st.text_input("Email address")
        submitted = st.form_submit_button(
            "Request verification email",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        email = email.strip().lower()
        if len(email) > 254 or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", email
        ):
            st.warning("Enter a valid email address.")
        else:
            try:
                message = resend_verification(API_BASE_URL, email)
                st.success(message)
            except requests.RequestException as exc:
                auth_request_error(exc)

    if st.button("Back to login"):
        st.session_state.auth_view = "login"
        st.rerun()


def show_verification():
    st.subheader("Verify your email")
    st.caption("Confirm your email address to activate your account.")

    token = st.session_state.pending_verify_token

    if not token:
        st.warning("No verification link was provided.")
    elif st.button(
        "Verify my email", type="primary", use_container_width=True
    ):
        # Remove the token from session state before the API request.
        st.session_state.pending_verify_token = None
        try:
            message = verify_account(API_BASE_URL, token)
            st.success(message)
            st.info("Your email is verified. You can now sign in.")
        except requests.RequestException as exc:
            auth_request_error(exc)
            st.info(
                "If verification did not complete, request a new "
                "verification email."
            )
        finally:
            del token

    if st.button("Go to login"):
        st.session_state.pending_verify_token = None
        st.session_state.auth_view = "login"
        st.rerun()

    if st.button("Request another verification email"):
        st.session_state.pending_verify_token = None
        st.session_state.auth_view = "resend"
        st.rerun()

def show_password_reset():
    token = st.session_state.pending_reset_token
    st.subheader("Choose a new password" if token else "Forgot password")
    with st.form("password_reset", clear_on_submit=True):
        if token:
            password = st.text_input("New password", type="password", help="Use at least 12 characters.")
            confirm = st.text_input("Confirm new password", type="password")
        else:
            email = st.text_input("Account email address", max_chars=254)
        submitted = st.form_submit_button(
            "Reset password" if token else "Send reset link", type="primary"
        )

    if submitted:
        if token and (len(password) < 12 or len(password.encode("utf-8")) > 72):
            st.warning("Use at least 12 characters and at most 72 bytes.")
        elif token and password != confirm:
            st.warning("The passwords must match.")
        elif not token and len(email.strip()) < 3:
            st.warning("Enter your account email address.")
        else:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/{'reset-password' if token else 'forgot-password'}",
                    json={"token": token, "password": password} if token else {"email": email.strip()},
                    timeout=15,
                )
                if token and response.status_code == 400:
                    st.error("This reset link is invalid or expired. Request a new link below.")
                else:
                    response.raise_for_status()
                    if token:
                        clear_user_session()
                        st.session_state.flash_message = response.json()["message"]
                        st.rerun()
                    st.success(response.json()["message"])
            except requests.RequestException as exc:
                auth_request_error(exc)

    if token and st.button("Request a new link"):
        st.session_state.pending_reset_token = None
        st.rerun()
    if st.button("Back to sign in"):
        st.session_state.pending_reset_token = None
        st.session_state.auth_view = "login"
        st.rerun()


def account_request(method, payload=None):
    response = requests.request(
        method, f"{API_BASE_URL}/account", headers=api_headers(), json=payload, timeout=15,
    )
    if response.status_code == 401:
        expire_session()
    return response


def show_account_settings():
    st.header("Account settings")
    try:
        response = account_request("GET")
        response.raise_for_status()
        profile = response.json()
    except requests.RequestException as exc:
        auth_request_error(exc)
        return

    st.text(f"Email address: {profile['email']}")
    if not profile["can_manage"]:
        st.caption("Demo accounts are managed by the administrator.")
        return

    with st.form("account_profile"):
        name = st.text_input("Full name", value=profile["full_name"], max_chars=100)
        save_name = st.form_submit_button("Save name", type="primary")

    if save_name:
        if not name.strip():
            st.warning("Enter your full name.")
        else:
            try:
                response = account_request("PATCH", {"full_name": name.strip()})
                response.raise_for_status()
                st.success("Name updated.")
            except requests.RequestException as exc:
                auth_request_error(exc)

    with st.expander("Delete account"):
        st.warning("This permanently deletes your account, saved reports, and research memory.")
        with st.form("delete_account", clear_on_submit=True):
            password = st.text_input("Current password", type="password")
            confirmed = st.checkbox("I understand this cannot be undone.")
            delete = st.form_submit_button("Permanently delete my account")

        if delete:
            if not password or not confirmed:
                st.warning("Enter your current password and confirm deletion.")
                return
            try:
                response = account_request("DELETE", {"password": password})
                if response.status_code == 400:
                    st.error("Could not confirm your current password.")
                    return
                response.raise_for_status()
                clear_user_session()
                st.session_state.flash_message = response.json()["message"]
                st.rerun()
            except requests.RequestException as exc:
                auth_request_error(exc)


if "reset_token" in st.query_params:
    reset_token = st.query_params["reset_token"]
    st.query_params.clear()
    if 0 < len(reset_token) <= 256:
        clear_user_session()
        st.session_state.pending_reset_token = reset_token
        st.session_state.auth_view = "forgot"


# Capture verification tokens and clear the URL immediately.
if "verify_token" in st.query_params:
    raw_token = st.query_params.get("verify_token", "")
    st.query_params.clear()

    if (
        not st.session_state.token
        and isinstance(raw_token, str)
        and 0 < len(raw_token) <= 256
    ):
        st.session_state.pending_verify_token = raw_token
        st.session_state.auth_view = "verify"
    else:
        st.session_state.pending_verify_token = None

# ─────────────────────────────────────────────────────────────────────────────
# Login — polished design, same POST /login contract.
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.token:
    display_topbar()
    st.markdown('<div class="tr-login-spacer"></div>', unsafe_allow_html=True)
    intro, sign_in = st.columns([1.12, 0.88], gap="large")

    with intro:
        st.markdown(
            '''<div class="tr-login-intro">
              <div class="tr-pill"><span class="tr-pulse"></span> INTELLIGENCE, NOT NOISE</div>
              <h1>Make smarter<br><span>market decisions.</span></h1>
              <p>One workspace for multi-agent research, market signals,
              news intelligence, sentiment and risk analysis.</p>
              <div class="tr-login-features">
                <div><span>01</span><strong>Multi-agent analysis</strong><small>Specialized research agents</small></div>
                <div><span>02</span><strong>Market intelligence</strong><small>Price, news &amp; sentiment</small></div>
                <div><span>03</span><strong>Research history</strong><small>Return to previous insights</small></div>
              </div>
              <div class="tr-stack-heading">
  ENGINEERED WITH MODERN AI TECHNOLOGIES
</div>
<div class="tr-tech-stack">
  <span>LangGraph</span>
  <span>RAG</span>
  <span>ChromaDB</span>
  <span>FastAPI</span>
  <span>Streamlit</span>
  <span>Python</span>
  <span>Docker</span>
  <span>AWS</span>
</div>
            </div>''',
            unsafe_allow_html=True,
        )


    with sign_in:
        if st.session_state.auth_view == "register":
            show_registration()

        elif st.session_state.auth_view == "resend":
            show_resend_verification()

        elif st.session_state.auth_view == "verify":
            show_verification()

        elif st.session_state.auth_view == "forgot":
            show_password_reset()

        else:
            st.markdown(
                '''<div class="tr-auth-heading">
                  <div class="tr-section-label">MEMBER ACCESS</div>
                  <h2>Welcome back</h2>
                  <p>Sign in to open your research workspace.</p>
                </div>''',
                unsafe_allow_html=True,
            )

            with st.form("login_form"):
                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )
                submitted = st.form_submit_button(
                    "Sign in to workspace",
                    type="primary",
                    use_container_width=True,
                )

            if st.session_state.flash_message:
                st.warning(st.session_state.flash_message)
                st.session_state.flash_message = None

            if submitted:
                if not email.strip() or not password:
                    st.warning("Enter both your email and password.")
                else:
                    try:
                        if login(email.strip(), password):
                            st.rerun()
                    except requests.HTTPError as exc:
                        display_login_error(exc)
                    except requests.Timeout:
                        st.error("Login request timed out.")
                    except requests.ConnectionError:
                        st.error("Cannot connect to FastAPI.")
                    except requests.RequestException:
                        st.error("An unexpected login error occurred.")

            if st.button("Forgot password?", use_container_width=True):
                st.session_state.auth_view = "forgot"
                st.rerun()

            if st.button(
                "Create a new account",
                use_container_width=True,
            ):
                st.session_state.auth_view = "register"
                st.rerun()

            if st.button(
                "Resend verification email",
                use_container_width=True,
            ):
                st.session_state.auth_view = "resend"
                st.rerun()

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# Logged-in workspace — sidebar, research, saved reports.
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.history_loaded:
    try:
        load_history()
    except requests.RequestException:
        st.session_state.history_loaded = False
        st.warning("Could not load saved reports from the API. You can retry from the sidebar.")

with st.sidebar:
    st.markdown(
        '<div class="tr-side-brand"><span class="tr-logo">◈</span>'
        '<span>AI TRADING <span class="tr-brand-accent">RESEARCH</span></span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="tr-section-label">WORKSPACE</div>', unsafe_allow_html=True)
    if st.button("＋  New research", type="primary", use_container_width=True):
        st.session_state.show_settings = False
        st.session_state.selected_report = None
        st.session_state.last_result = None
        st.session_state.last_query = ""
        st.rerun()

    st.markdown('<div class="tr-section-label tr-history-heading">SAVED RESEARCH</div>', unsafe_allow_html=True)
    if st.button("↻  Refresh history", use_container_width=True):
        try:
            load_history()
            st.rerun()
        except requests.HTTPError as exc:
            display_history_error(exc)
        except requests.Timeout:
            st.error("History request timed out. Please try again.")
        except requests.RequestException:
            st.error("Cannot connect to the API.")

    history = st.session_state.history
    if not history:
        st.caption("No saved reports loaded yet.")
    else:
        for item in history:
            title = str(item.get("query") or "Untitled research").strip()
            date = str(item.get("created_at") or "")[:10]
            short_title = title[:38] + ("…" if len(title) > 38 else "")
            label = f"{short_title}\n{date}" if date else short_title
            if st.button(
                label,
                key=f"history_{item['id']}",
                use_container_width=True,
            ):
                st.session_state.show_settings = False
                st.session_state.selected_report = item
                st.rerun()

    st.divider()
    st.markdown('<div class="tr-section-label">SIGNED IN AS</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="tr-account"><span class="tr-avatar">●</span>'
        f'<span>{escape(str(st.session_state.email or ""))}</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("Account settings", use_container_width=True):
        st.session_state.show_settings = True
        st.rerun()
    if st.button("Log out  ↗", use_container_width=True):
        logout()


if st.session_state.show_settings:
    show_account_settings()
    st.stop()


selected = st.session_state.selected_report
if selected:
    st.markdown(
        '''<div class="tr-hero">
          <div class="tr-eyebrow">RESEARCH LIBRARY / SAVED REPORT</div>
          <h1>Revisit your insights.</h1>
          <p>Your previous market analysis, ready whenever you need it.</p>
        </div>''',
        unsafe_allow_html=True,
    )
    st.caption(f"Research question: {selected.get('query', 'Untitled research')}")
    left, _ = st.columns([1, 4])
    with left:
        if st.button("←  Back to research", use_container_width=True):
            st.session_state.selected_report = None
            st.rerun()
    render_report(selected.get("result"), "Saved research report")
    st.caption(f"Saved at: {selected.get('created_at', 'Unknown date')}")

else:
    st.markdown(
        '''<div class="tr-hero">
          <div class="tr-eyebrow"><span class="tr-pulse"></span> AI-POWERED MARKET INTELLIGENCE</div>
          <h1>Your research. <span style="color:#45e2ca">Elevated.</span></h1>
          <p>Explore the market through price data, news, sentiment and risk —
          brought together by specialized AI agents.</p>
        </div>''',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="tr-section-label">RESEARCH WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown("### What would you like to analyze?")
    st.caption("Ask a detailed question about an asset, market trend, or investment risk.")

    with st.form("research_form"):
        query = st.text_area(
            "Your research question",
            placeholder=(
                "Example: Analyze BTC-USD market sentiment, recent news, "
                "price movements and the key risks to watch."
            ),
            height=135,
        )
        submitted = st.form_submit_button(
            "✦  Generate research report", type="primary", use_container_width=True,
        )

    st.markdown(
        '''<div class="tr-feature-strip">
          <div><span>📈</span><strong>Price intelligence</strong><small>Market context</small></div>
          <div><span>📰</span><strong>News analysis</strong><small>Relevant developments</small></div>
          <div><span>🧠</span><strong>Sentiment signals</strong><small>Market perspective</small></div>
          <div><span>🛡️</span><strong>Risk assessment</strong><small>Key considerations</small></div>
        </div>''',
        unsafe_allow_html=True,
    )

    if submitted:
        if not query.strip():
            st.warning("Enter a research question first.")
        else:
            try:
                with st.spinner("Research agents are analyzing market data, news, sentiment and risk..."):
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
                st.session_state.last_result = result
                st.session_state.last_query = query.strip()
                st.success("Research completed. Your report is ready below.")
                try:
                    load_history()
                except requests.RequestException:
                    st.warning("Report generated, but saved history could not be refreshed.")
            except requests.HTTPError as exc:
                display_research_error(exc)
            except requests.Timeout:
                st.error(
                    "The research request timed out. "
                    "Check whether the backend is still processing it."
                )
            except requests.RequestException:
                st.error("Could not reach the API. Verify that FastAPI is running.")

    if st.session_state.last_result is not None:
        st.divider()
        st.caption(f"Research question: {st.session_state.last_query}")
        render_report(st.session_state.last_result)


st.markdown(
    """
    <div class="tr-footer">
        <strong>AI TRADING RESEARCH AGENT</strong><br>
        Built with Python · Streamlit · FastAPI · LangGraph · RAG · ChromaDB<br>
        Deployed on AWS · Docker · GitHub Actions
    </div>
    """,
    unsafe_allow_html=True,
)
