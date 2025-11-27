import os
import sys
from pathlib import Path

# --- Make project root importable so `import src.*` works ---
# This file lives at: <project_root>/src/streamlit_app/app.py
# We want to add <project_root> to sys.path so `import src...` succeeds.
THIS_FILE = os.path.abspath(__file__)
SRC_DIR = os.path.dirname(os.path.dirname(THIS_FILE))        # .../Bonus Assignment 1/src
PROJECT_ROOT = os.path.dirname(SRC_DIR)                      # .../Bonus Assignment 1

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from src.agentic.workflow import build_graph

st.set_page_config(page_title="Bonus Assignment 1 – GitHub Agentic Analytics", layout="wide")

st.title("Bonus Assignment 1 – Agentic GitHub Analytics")

st.markdown(
    """
This app lets you ask natural-language questions about GitHub repositories
and their issues/pull requests, using:

- PostgreSQL as the data store  
- LangGraph + Python REPL as the agentic backend  
- `gpt-4o-mini` (or compatible) as the LLM  

**Examples you should try (these map to the assignment questions):**

1. *Which repo has the highest number of issues created?*  
2. *Create a table of total number of issues created per day of week for each repo.*  
3. *Plot a line chart of number of issues created per day for each repo.*  
4. *Plot a pie chart of percentage of issues created per repo.*  
5. *Plot a bar chart of each repo with stars and forks.*  
6. *Plot a bar chart of total number of issues closed in last 7, 14, 30, 60 days per repo.*  
7. *Plot a stacked bar chart of issues created and closed per repo.*  
8. *Using Prophet, forecast next 30 days of issues created per repo.*  
9. *Using Statsmodels, build a time-series model for issues created per repo.*  
"""
)

default_prompt = st.session_state.get("prefill_prompt", "")

user_query = st.text_area("User Input Prompt", value=default_prompt, height=140)

with st.expander("Quick assignment queries"):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Q1 – Highest # issues created"):
            st.session_state["prefill_prompt"] = "Which repo has the highest number of issues created?"
            st.rerun()
        if st.button("Q2 – Issues created by day of week per repo"):
            st.session_state["prefill_prompt"] = (
                "Create a table of total number of issues created, created day of week, "
                "and their day of week for each repo."
            )
            st.rerun()
        if st.button("Q3 – Line chart issues per day per repo"):
            st.session_state["prefill_prompt"] = (
                "Plot a line chart of total number of issues created per day for each repo."
            )
            st.rerun()
        if st.button("Q4 – Pie chart issues share per repo"):
            st.session_state["prefill_prompt"] = (
                "Plot a pie chart of percentage of issues created for each repo."
            )
            st.rerun()
    with col2:
        if st.button("Q5 – Stars & forks per repo"):
            st.session_state["prefill_prompt"] = (
                "Plot a bar chart of each repo showing stars and forks."
            )
            st.rerun()
        if st.button("Q6 – Issues closed in last 7/14/30/60 days"):
            st.session_state["prefill_prompt"] = (
                "Plot bar charts of total number of issues closed in last 7, 14, 30, and 60 days per repo."
            )
            st.rerun()
        if st.button("Q7 – Stacked created vs closed"):
            st.session_state["prefill_prompt"] = (
                "Plot a stacked bar chart showing issues created and issues closed for each repo."
            )
            st.rerun()
        if st.button("Q8/Q9 – Forecast issues with Prophet & Statsmodels"):
            st.session_state["prefill_prompt"] = (
                "Using Prophet and Statsmodels, build time series models for issues created per repo "
                "and forecast the next 30 days."
            )
            st.rerun()

run_btn = st.button("Run Agent")

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()

if run_btn and user_query.strip():
    with st.spinner("Thinking with LLM + Python REPL..."):
        graph = st.session_state.graph
        state = graph.invoke({"question": user_query, "messages": [], "result": ""})
        result_text = state.get("result", "")

    st.subheader("Text / Table Response")
    if result_text:
        st.write(result_text)
    else:
        st.info("The agent did not return a textual result. Check logs or try a different query.")

    chart_path = Path("chart.png")
    if chart_path.exists():
        st.subheader("Chart Response")
        st.image(str(chart_path))
    else:
        st.caption("No chart was generated for this query.")
