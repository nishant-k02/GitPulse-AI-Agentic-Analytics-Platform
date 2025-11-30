import os
import sys
import re
from pathlib import Path

# --- Make `src` importable so we can do `from agentic import ...` ---
THIS_FILE = os.path.abspath(__file__)
STREAMLIT_DIR = os.path.dirname(THIS_FILE)        # .../Bonus Assignment 1/src/streamlit_app
SRC_DIR = os.path.dirname(STREAMLIT_DIR)          # .../Bonus Assignment 1/src

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import streamlit as st
from agentic.workflow import build_graph


# ------------------ Streamlit page config ------------------

st.set_page_config(
    page_title="GitHub Agentic Analytics",
    layout="wide",
)

# ------------------ Modern UI Styling ------------------

st.markdown(
    """
    <style>
        /* Reduce overall padding */
        .block-container {
            padding-top: 0.8rem !important;
            padding-bottom: 0.5rem !important;
        }

        /* HEADER */
        .app-header {
            width: 100%;
            padding: 1.3rem 0rem 1.4rem 0rem;
            background: linear-gradient(90deg, #1e293b, #0f172a);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 1.4rem;
        }
        .app-header h1 {
            text-align: center;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            margin: 0;
            color: #eef2ff;
        }
        .app-header h3 {
            text-align: center;
            font-weight: 400 !important;
            font-size: 1.05rem !important;
            margin-top: 0.25rem;
            color: #cbd5e1;
        }

        /* FOOTER */
        .footer {
            width: 100%;
            margin-top: 2.5rem;
            padding: 0.6rem 0rem;
            text-align: center;
            font-size: 0.83rem;
            color: rgba(209, 213, 219, 0.65);
            border-top: 1px solid rgba(255,255,255,0.08);
        }
        .footer a {
            color: #93c5fd;
            text-decoration: none;
        }

        /* Card UI */
        .card {
            padding: 1.2rem 1.4rem;
            border-radius: 0.8rem;
            border: 1px solid rgba(255,255,255,0.07);
            background: rgba(30, 41, 59, 0.45);
        }

        /* Buttons */
        .stButton > button {
            width: 100%;
            border-radius: 999px;
            padding: 0.55rem 1rem;
            border: 1px solid rgba(148,163,184,0.5);
            background: rgba(37, 99, 235, 0.88);
            transition: 0.2s ease;
        }
        .stButton > button:hover {
            border-color: rgba(191,219,254,1);
            background: rgb(59, 130, 246);
        }

        /* Small caption */
        .small-caption {
            font-size: 0.82rem !important;
            color: rgba(148, 163, 184, 0.9);
        }

        /* Code font size */
        code, pre {
            font-size: 0.85rem !important;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------ HEADER ------------------

st.markdown(
    """
    <div class="app-header">
        <h1>📊 GitHub Agentic Analytics</h1>
        <h3>LLM-powered analytics · Python REPL · Forecasting · SQL Automation</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------ Description Card ------------------

st.markdown(
    """
<div class='card'>
    Ask natural language questions.  
    The agent generates Python + SQL → executes → shows results and charts.
    <ul>
        <li>LLM → Python + SQL Generation</li>
        <li>Polars / Pandas → Execution Engine</li>
        <li>Prophet & StatsModels → Forecasting</li>
        <li>Matplotlib → Visualization</li>
    </ul>
</div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")

# ------------------ Input area ------------------

default_prompt = st.session_state.get("prefill_prompt", "")

input_col, run_col = st.columns([4, 1])

with input_col:
    user_query = st.text_area(
        "📝 Your Query",
        value=default_prompt,
        height=140,
        placeholder="E.g., 'Which repo has the highest number of issues created?'",
    )

with run_col:
    st.markdown("&nbsp;", unsafe_allow_html=True)
    run_btn = st.button("🚀 Run Agent", use_container_width=True)

expect_chart_from_button = False

# ------------------ Quick Queries ------------------

with st.expander("⚡ Quick Assignment Queries", expanded=False):

    st.markdown("<div class='small-caption'>Q6 = Text · Q7 = Charts</div>", unsafe_allow_html=True)

    col_text, col_charts = st.columns(2)

    with col_text:
        st.markdown("### **Q6 – Text Queries**")
        if st.button("Q6.1 – Highest # issues created"):
            st.session_state["prefill_prompt"] = "Which Repo has the highest number of issues created?"
            st.session_state["expect_chart_flag"] = False
            st.rerun()

        if st.button("Q6.2 – Issues per repo/day-of-week"):
            st.session_state["prefill_prompt"] = (
                "Create a table of the total number of issues created for every repo for every day of the week; "
                "that is, total number of issues created on Monday, Tuesday, Wednesday … Sunday for EVERY repo name."
            )
            st.session_state["expect_chart_flag"] = False
            st.rerun()

        if st.button("Q6.3 – Most issues created (ALL repos)"):
            st.session_state["prefill_prompt"] = "Which day of the week has the highest number of total issues created for ALL repos?"
            st.session_state["expect_chart_flag"] = False
            st.rerun()

        if st.button("Q6.4 – Most issues closed (ALL repos)"):
            st.session_state["prefill_prompt"] = "Which day of the week has the highest number of total issues closed for ALL repos?"
            st.session_state["expect_chart_flag"] = False
            st.rerun()

    with col_charts:
        st.markdown("### **Q7 – Chart Queries**")
        if st.button("Q7.1 – Line chart: total issues over time"):
            st.session_state["prefill_prompt"] = "Plot a line chart of total issues created over time."
            st.session_state["expect_chart_flag"] = True
            st.rerun()

        if st.button("Q7.2 – Pie chart: issue distribution"):
            st.session_state["prefill_prompt"] = "What is the percentage distribution (create Pie Chart) of issues created."
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


expect_chart_from_button = st.session_state.get("expect_chart_flag", False)

st.markdown("---")


# ------------------ Graph init ------------------

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()


# ------------------ Code Extractor ------------------

def extract_code_from_messages(messages):
    if not messages:
        return ""
    last = messages[-1]
    raw = getattr(last, "content", "")
    if not isinstance(raw, str):
        raw = str(raw)
    m = re.search(r"```python(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"```(.*?)```", raw, re.DOTALL)
    if m:
        return m.group(1).strip()
    return raw.strip()


# ------------------ Run Agent ------------------

if run_btn and user_query.strip():

    chart_path = Path("chart.png")
    if chart_path.exists():
        try:
            chart_path.unlink()
        except:
            pass

    with st.spinner("🔍 Thinking… Generating Python + SQL… Executing…"):
        graph = st.session_state.graph
        state = graph.invoke({"question": user_query, "messages": [], "result": ""})

        result_text = state.get("result", "")
        generated_code = extract_code_from_messages(state.get("messages", []))

    # Detect chart-intent
    q_lower = user_query.lower()
    chart_keywords = [
        "plot", "chart", "graph", "line chart", "bar chart",
        "pie", "histogram", "stack", "stacked",
        "forecast", "prophet", "statsmodel"
    ]
    asked_for_chart = any(k in q_lower for k in chart_keywords)
    should_show_chart = expect_chart_from_button or asked_for_chart

    # Columns layout
    code_col, out_col = st.columns([1.05, 1.35])

    with code_col:
        st.subheader("🧠 Generated Python Code")
        st.code(generated_code, language="python")

    with out_col:
        st.subheader("📄 Text / Table Output")
        st.write(result_text)

        # Chart display
        if should_show_chart and Path("chart.png").exists():
            st.subheader("📈 Chart Output")
            st.image("chart.png")
        else:
            st.markdown("<div class='small-caption'>No chart generated for this query.</div>", unsafe_allow_html=True)
