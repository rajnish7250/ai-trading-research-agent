"""Visual theme for the AI Trading Research Agent Streamlit frontend.

UI-only module. Does not call APIs, access the database, or change authentication.
Usage in streamlit_app.py, AFTER st.set_page_config(...):

    from ui_theme import apply_theme
    apply_theme()
"""

import streamlit as st


_THEME_CSS = r"""
<style>
:root {
  --tr-bg: #080f1f;
  --tr-surface: #101d33;
  --tr-surface-2: #14253d;
  --tr-border: rgba(144, 172, 205, 0.17);
  --tr-text: #eaf4ff;
  --tr-muted: #a2b4ca;
  --tr-accent: #2de1c2;
  --tr-accent-blue: #4c9aff;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
  color: var(--tr-text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
}

.stApp, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 60% 42% at 78% -12%, rgba(39, 117, 179, .22), transparent 72%),
    radial-gradient(ellipse 42% 32% at 7% 4%, rgba(19, 147, 141, .12), transparent 70%),
    linear-gradient(160deg, #080e1d 0%, #0a1427 58%, #0a1729 100%);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"] { display: none; }

.block-container {
  max-width: 1180px;
  padding-top: 2.6rem;
  padding-bottom: 4rem;
}

h1, h2, h3, h4, h5, h6 { color: #f2f8ff !important; letter-spacing: -.035em; }
h1 { font-weight: 800 !important; line-height: 1.15 !important; }
h2, h3 { font-weight: 730 !important; }
p, label, .stMarkdown { line-height: 1.65; }
[data-testid="stCaptionContainer"], small { color: var(--tr-muted) !important; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #101d32 0%, #0b1628 100%);
  border-right: 1px solid var(--tr-border);
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .65rem; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f2f8ff !important; }
[data-testid="stSidebar"] hr { border-color: var(--tr-border); }

/* Forms and input fields */
[data-testid="stForm"] {
  background: linear-gradient(145deg, rgba(20, 39, 62, .91), rgba(12, 25, 44, .94));
  border: 1px solid var(--tr-border);
  border-radius: 20px;
  padding: 1.35rem 1.4rem 1.1rem;
  box-shadow: 0 18px 45px rgba(0, 0, 0, .17);
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="input"] input {
  background: rgba(8, 20, 37, .92) !important;
  border: 1px solid rgba(142, 174, 210, .24) !important;
  border-radius: 11px !important;
  color: #f0f7ff !important;
  caret-color: var(--tr-accent);
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: rgba(45, 225, 194, .75) !important;
  box-shadow: 0 0 0 2px rgba(45, 225, 194, .12) !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #8195ae !important; }
[data-testid="stWidgetLabel"] label { color: #c5d6e8 !important; font-weight: 600; }

/* Primary and secondary buttons */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"] {
  background: linear-gradient(105deg, #2ce1c0 0%, #27b9e1 100%) !important;
  border: 1px solid transparent !important;
  color: #071a2a !important;
  font-weight: 760 !important;
  box-shadow: 0 7px 22px rgba(32, 207, 193, .17);
}
.stButton > button,
.stFormSubmitButton > button {
  border-radius: 11px !important;
  min-height: 2.75rem;
  transition: transform .15s ease, border-color .15s ease, box-shadow .15s ease;
  font-weight: 650;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover {
  transform: translateY(-1px);
  border-color: #2de1c2 !important;
  box-shadow: 0 7px 24px rgba(32, 207, 193, .13);
}
.stButton > button[kind="secondary"],
.stFormSubmitButton > button[kind="secondary"] {
  background: rgba(20, 39, 62, .8) !important;
  color: #e3effd !important;
  border: 1px solid rgba(142, 174, 210, .25) !important;
}

/* Results and status */
[data-testid="stExpander"] {
  background: linear-gradient(145deg, rgba(21, 40, 64, .83), rgba(13, 27, 46, .93));
  border: 1px solid var(--tr-border);
  border-radius: 15px;
  overflow: hidden;
  margin-bottom: .55rem;
}
[data-testid="stExpander"] summary { padding: .35rem .65rem; font-weight: 650; }
[data-testid="stMetric"] {
  background: rgba(20, 39, 62, .78);
  border: 1px solid var(--tr-border);
  border-radius: 15px;
  padding: 1rem 1.15rem;
}
[data-testid="stMetricValue"] { color: var(--tr-accent) !important; }
[data-testid="stAlert"] { border-radius: 12px; }
[data-testid="stJson"] { border-radius: 12px; overflow: hidden; }
[data-testid="stDataFrame"] { border-radius: 13px; overflow: hidden; }
[data-testid="stTabs"] [role="tablist"] { gap: .35rem; }
[data-testid="stTabs"] button[role="tab"] { border-radius: 9px 9px 0 0; font-weight: 650; }
[data-testid="stTabs"] button[aria-selected="true"] { color: var(--tr-accent) !important; }
hr { border-color: var(--tr-border) !important; }
a { color: #69dbe7; }

/* Optional reusable hero/card classes for future layout work */
.tr-hero {
  position: relative;
  overflow: hidden;
  padding: 2rem 2.2rem;
  border-radius: 22px;
  border: 1px solid rgba(100, 184, 207, .23);
  background: linear-gradient(115deg, rgba(20, 57, 75, .95), rgba(16, 30, 56, .98) 62%, rgba(13, 34, 56, .98));
  box-shadow: 0 18px 55px rgba(0, 0, 0, .15);
  margin-bottom: 1.5rem;
}
.tr-hero:after {
  content: "";
  position: absolute;
  width: 250px;
  height: 250px;
  border-radius: 50%;
  right: -90px;
  top: -110px;
  background: radial-gradient(circle, rgba(45, 225, 194, .16), transparent 70%);
  pointer-events: none;
}
.tr-eyebrow { font-size: .75rem; text-transform: uppercase; letter-spacing: .16em; color: #66e6d1; font-weight: 800; }
.tr-hero h1 { margin: .5rem 0 .4rem; font-size: clamp(1.7rem, 4vw, 2.8rem); }
.tr-hero p { color: #aec5d8; margin: 0; max-width: 700px; }
.tr-card {
  padding: 1.25rem 1.35rem;
  background: linear-gradient(150deg, rgba(20, 40, 63, .88), rgba(13, 26, 45, .94));
  border: 1px solid var(--tr-border);
  border-radius: 16px;
}

@media (max-width: 768px) {
  .block-container { padding-top: 1.5rem; padding-left: 1rem; padding-right: 1rem; }
  .tr-hero { padding: 1.4rem; border-radius: 16px; }
  [data-testid="stForm"] { padding: 1rem; }
}
@media (prefers-reduced-motion: reduce) {
  .stButton > button, .stFormSubmitButton > button { transition: none; }
  .stButton > button:hover, .stFormSubmitButton > button:hover { transform: none; }
}

/* New polished frontend elements */
.tr-topbar {display:flex;align-items:center;gap:.7rem;padding:.3rem 0 1.2rem;border-bottom:1px solid rgba(137,171,209,.13);margin-bottom:1rem}
.tr-logo {display:inline-flex;align-items:center;justify-content:center;width:35px;height:35px;background:linear-gradient(140deg,#38e5c5,#3d9af5);border-radius:10px;color:#071827;font-size:1.45rem;font-weight:900;flex-shrink:0}
.tr-brand,.tr-side-brand {font-weight:850;letter-spacing:.075em;color:#f0f8ff;font-size:.91rem}
.tr-brand-accent {color:#4be2ce}
.tr-topbar-tag {margin-left:auto;color:#839db9;font-size:.68rem;letter-spacing:.14em;font-weight:750}
.tr-login-spacer {height:clamp(1rem,5vh,4rem)}
.tr-login-intro {padding:1.8rem 1.6rem 2rem 0}
.tr-pill {display:inline-flex;align-items:center;gap:.55rem;border:1px solid rgba(75,226,206,.28);background:rgba(25,123,123,.13);padding:.5rem .75rem;border-radius:30px;color:#62e7d4;font-size:.67rem;font-weight:800;letter-spacing:.13em}
.tr-pulse {display:inline-block;width:7px;height:7px;border-radius:50%;background:#4ae2b8;box-shadow:0 0 0 4px rgba(74,226,184,.12);margin-right:.2rem}
.tr-login-intro h1 {font-size:clamp(2.6rem,4.9vw,4.8rem)!important;line-height:1.08!important;letter-spacing:-.065em!important;margin:1.35rem 0 1.2rem!important;font-weight:850!important}
.tr-login-intro h1 span {background:linear-gradient(100deg,#49e7c7,#61a7ff);-webkit-background-clip:text;background-clip:text;color:transparent}
.tr-login-intro p {color:#a9bed3;max-width:490px;font-size:1.06rem;line-height:1.8}
.tr-login-features {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.65rem;margin-top:2.5rem}
.tr-login-features>div {display:flex;flex-direction:column;gap:.35rem;padding:1rem .9rem;border:1px solid rgba(137,171,209,.17);border-radius:13px;background:rgba(18,37,60,.7)}
.tr-login-features span {font-size:.7rem;color:#4be2ce;font-weight:850}
.tr-login-features strong {font-size:.82rem;color:#eaf5ff;line-height:1.3}
.tr-login-features small {font-size:.73rem;color:#8ba5bf;line-height:1.4}
.tr-fineprint {margin-top:2.5rem;font-size:.68rem;letter-spacing:.15em;color:#738eaa;font-weight:750}
.tr-auth-heading {margin:.7rem 0 1.2rem}
.tr-auth-heading h2 {font-size:2rem;margin:.55rem 0 .25rem!important}
.tr-auth-heading p {color:#9bb2ca;margin:0}
.tr-section-label {color:#4cddc7;font-size:.69rem;letter-spacing:.16em;font-weight:850;margin:1rem 0 .65rem}
.tr-side-brand {display:flex;align-items:center;gap:.65rem;margin:0 0 2.2rem}
.tr-side-brand .tr-logo {width:32px;height:32px;font-size:1.3rem}
.tr-history-heading {margin-top:2rem}
.tr-account {display:flex;align-items:center;gap:.7rem;padding:.8rem;border-radius:12px;background:rgba(34,57,79,.5);border:1px solid rgba(137,171,209,.13);color:#d4e5f4;font-size:.79rem;overflow-wrap:anywhere}
.tr-avatar {width:29px;height:29px;border-radius:50%;background:#183e49;color:#43d9c5;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0}
.tr-feature-strip {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.75rem;margin:1.1rem 0 2rem}
.tr-feature-strip>div {display:flex;flex-direction:column;gap:.28rem;border:1px solid rgba(137,171,209,.17);border-radius:14px;background:rgba(17,36,59,.62);padding:1rem}
.tr-feature-strip span {font-size:1.3rem;margin-bottom:.15rem}
.tr-feature-strip strong {font-size:.83rem;color:#e5f4ff}
.tr-feature-strip small {font-size:.73rem;color:#8da9c1}
.tr-footer {font-size:.68rem;color:#718ba5;letter-spacing:.13em;font-weight:700;padding:2rem 0 1rem;border-top:1px solid rgba(137,171,209,.12);margin-top:2.5rem;text-align:center}
[data-testid="stSidebar"] .stButton>button {text-align:left;white-space:pre-wrap;line-height:1.35;height:auto;min-height:2.75rem}
[data-testid="stSidebar"] .stButton>button p {white-space:pre-wrap;overflow-wrap:anywhere}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {padding-top:1.4rem}
[data-testid="stForm"] {padding:1.5rem}
[data-testid="stTabs"] [role="tablist"] {overflow-x:auto;flex-wrap:nowrap}
[data-testid="stTabs"] button[role="tab"] {white-space:nowrap}
@media (max-width:950px) {
  .tr-login-features {grid-template-columns:1fr}
  .tr-feature-strip {grid-template-columns:repeat(2,minmax(0,1fr))}
  .tr-login-intro {padding-right:0}
}
@media (max-width:640px) {
  .tr-topbar-tag {display:none}
  .tr-login-intro h1 {font-size:2.7rem!important}
  .tr-login-features {grid-template-columns:repeat(3,minmax(0,1fr))}
  .tr-login-features>div {padding:.75rem .55rem}
  .tr-login-features strong {font-size:.7rem}
  .tr-login-features small {font-size:.65rem}
  .tr-feature-strip {grid-template-columns:repeat(2,minmax(0,1fr))}
}
/* Primary action buttons: teal gradient */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(105deg, #2de1c2, #27b9e1) !important;
    color: #071a2a !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 11px !important;
}

[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(105deg, #48efd2, #55c9f0) !important;
    color: #071a2a !important;
}

/* Improve readability */
.tr-footer {
    font-size: 0.83rem;
    letter-spacing: 0.06em;
}

.tr-section-label {
    font-size: 0.78rem;
}

[data-testid="stSidebar"] .stButton button {
    font-size: 0.88rem;
}
.tr-stack-heading {
    margin-top: 28px;
    margin-bottom: 12px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: #89A8C8;
}

.tr-tech-stack {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.tr-tech-stack span {
    padding: 7px 12px;
    background: #142840;
    border: 1px solid #2D4962;
    border-radius: 8px;
    color: #BCE8EC;
    font-size: 0.78rem;
    font-weight: 600;
}
</style>
"""


def apply_theme() -> None:
    """Inject dark visual styling. Call after st.set_page_config()."""
    st.markdown(_THEME_CSS, unsafe_allow_html=True)
