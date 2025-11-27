import os
import sys
import re
from pathlib import Path

# --- Make project root importable so `import src.*` works ---
THIS_FILE = os.path.abspath(__file__)
SRC_DIR = os.path.dirname(os.path.dirname(THIS_FILE))  # .../Bonus Assignment 1/src
PROJECT_ROOT = os.path.dirname(SRC_DIR)                # .../Bonus Assignment 1

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from src.agentic.workflow import build_graph


# ------------------ Streamlit page config ------------------

st.set_page_config(
    page_title="GitHub Agentic Analytics",
    layout="wide",
)

# ------------- Lightweight custom styling (modern look) -------------

st.markdown(
    """
    <style>
    /* Overall page */
    .main {
        padding-top: 1.5rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
    /* Headings */
    h1, h2, h3 {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }
    /* Cards */
    .card {
        padding: 1.25rem 1.5rem;
        border-radius: 0.8rem;
        border: 1px solid rgba(250, 250, 250, 0.08);
        background: rgba(17, 24, 39, 0.75);
    }
    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 999px;
        padding: 0.45rem 0.9rem;
        font-size: 0.85rem;
        border: 1px solid rgba(148, 163, 184, 0.6);
        background: rgba(30, 64, 175, 0.9);
    }
    .stButton > button:hover {
        border-color: rgba(191, 219, 254, 1);
        background: rgba(37, 99, 235, 1);
    }
    /* Code block tweaks */
    pre, code {
        font-size: 0.85rem !important;
        line-height: 1.4 !important;
    }
    /* Subtle captions */
    .small-caption {
        font-size: 0.8rem;
        color: rgba(148, 163, 184, 0.9);
        margin-top: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ Page header ------------------

st.markdown("### 📊 GitHub Agentic Analytics – Bonus Assignment 1")
st.markdown(
    """
    Ask **natural-language questions** about GitHub repositories and their issues / PRs.

    Under the hood this app uses:

    - A **foundation model** to generate Python + SQL code
    - A **Python REPL** + `run_sql_pl()` to execute against PostgreSQL
    - Matplotlib / Prophet / Statsmodels for charts & time-series

    Below you’ll see the **generated code** on the left and the **answer / chart** on the right.
    """
)

st.markdown("---")

# ------------------ Input area ------------------

default_prompt = st.session_state.get("prefill_prompt", "")

input_col, run_col = st.columns([4, 1])

with input_col:
    user_query = st.text_area(
        "📝 User Input Prompt",
        value=default_prompt,
        height=150,
        placeholder="E.g., 'Which repo has the highest number of issues created?'",
    )

with run_col:
    st.markdown("<div style='margin-top:85px;'>", unsafe_allow_html=True)
    run_btn = st.button("🚀 Run Agent", use_container_width=True)

# Flag: did user trigger via a chart quick-button?
expect_chart_from_button = False

# ------------------ Quick assignment queries ------------------

with st.expander("⚡ Quick assignment queries", expanded=False):
    st.markdown(
        "<div class='small-caption'>Q6 → text / tables · Q7 → visualizations</div>",
        unsafe_allow_html=True,
    )
    col_text, col_charts = st.columns(2)

    with col_text:
        st.markdown("**Q6 – Text / Table**")
        if st.button("Q6.1 – Highest # issues created"):
            st.session_state["prefill_prompt"] = "Which Repo has the highest number of issues created?"
            st.session_state["expect_chart_flag"] = False
            st.rerun()
        if st.button("Q6.2 – Issues per repo per day-of-week (table)"):
            st.session_state["prefill_prompt"] = (
                "Create a table of the total number of issues created for every repo for every day of the week; "
                "that is, total number of issues created on Monday, Tuesday, Wednesday … Sunday for EVERY repo name."
            )
            st.session_state["expect_chart_flag"] = False
            st.rerun()
        if st.button("Q6.3 – Day with most issues created (ALL repos)"):
            st.session_state["prefill_prompt"] = (
                "Which day of the week has the highest number of total issues created for ALL repos?"
            )
            st.session_state["expect_chart_flag"] = False
            st.rerun()
        if st.button("Q6.4 – Day with most issues closed (ALL repos)"):
            st.session_state["prefill_prompt"] = (
                "Which day of the week has the highest number of total issues closed for ALL repos?"
            )
            st.session_state["expect_chart_flag"] = False
            st.rerun()

    with col_charts:
        st.markdown("**Q7 – Charts**")
        if st.button("Q7.1 – Line chart: total issues over time"):
            st.session_state["prefill_prompt"] = "Plot a line chart of total issues created over time."
            st.session_state["expect_chart_flag"] = True
            st.rerun()
        if st.button("Q7.2 – Pie chart: issues distribution"):
            st.session_state["prefill_prompt"] = (
                "What is the percentage distribution (create Pie Chart) of issues created."
            )
            st.session_state["expect_chart_flag"] = True
            st.rerun()
        if st.button("Q7.3 – Stars per repo (bar)"):
            st.session_state["prefill_prompt"] = "Create a Bar Chart to plot the stars for every Repo."
            st.session_state["expect_chart_flag"] = True
            st.rerun()
        if st.button("Q7.4 – Forks per repo (bar)"):
            st.session_state["prefill_prompt"] = "Create a Bar Chart to plot the forks for every Repo."
            st.session_state["expect_chart_flag"] = True
            st.rerun()

# Recover flag if set earlier
expect_chart_from_button = st.session_state.get("expect_chart_flag", False)

st.markdown("---")

# ------------------ Graph init ------------------

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()


# ------------------ Helper: extract code from messages ------------------

def extract_code_from_messages(messages) -> str:
    """Pull the last AI message and extract the python code block, if present."""
    if not messages:
        return ""

    last = messages[-1]
    raw = getattr(last, "content", "")

    if not isinstance(raw, str):
        raw = str(raw)

    # ```python ... ``` or ``` ... ```
    m = re.search(r"```python(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()

    m = re.search(r"```(.*?)```", raw, re.DOTALL)
    if m:
        return m.group(1).strip()

    return raw.strip()


# ------------------ Run + display results ------------------

if run_btn and user_query.strip():
    # Remove any old chart so we don't show stale images
    chart_path = Path("chart.png")
    if chart_path.exists():
        try:
            chart_path.unlink()
        except OSError:
            # If some process is locking it, we just leave it; better than crashing
            pass

    with st.spinner("Running LLM → generating Python → executing in REPL…"):
        graph = st.session_state.graph
        state = graph.invoke({"question": user_query, "messages": [], "result": ""})
        result_text = state.get("result", "")
        generated_code = extract_code_from_messages(state.get("messages", []))

    # Decide if we *should* show a chart for THIS query
    q_lower = user_query.lower()
    chart_keywords = [
        "plot",
        "chart",
        "graph",
        "line chart",
        "bar chart",
        "pie",
        "histogram",
        "stack",
        "stacked",
        "forecast",
        "prophet",
        "statsmodel",
    ]
    asked_for_chart = any(k in q_lower for k in chart_keywords)
    should_show_chart = expect_chart_from_button or asked_for_chart

    # Layout: left = code, right = outputs
    code_col, out_col = st.columns([1.05, 1.35])

    with code_col:
        st.subheader("🧠 Generated Python Code")
        with st.container():
            if generated_code:
                st.code(generated_code, language="python")
            else:
                st.info("No code was found in the LLM response.")

    with out_col:
        st.subheader("📄 Text / Table Response")
        with st.container():
            if result_text:
                st.write(result_text)
            else:
                st.warning(
                    "The agent did not return a textual result. "
                    "Check the generated code or try a different query."
                )

        # Chart section
        st.markdown("")
        if should_show_chart and chart_path.exists():
            st.subheader("📈 Chart Response")
            st.image(str(chart_path))
        elif chart_path.exists() and not should_show_chart:
            st.markdown(
                "<div class='small-caption'>"
                "A chart was generated internally, but your query didn't explicitly ask for a visualization. "
                "Include words like <code>plot</code> or <code>chart</code> if you want to see it here."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='small-caption'>No chart was generated for this query.</div>",
                unsafe_allow_html=True,
            )
