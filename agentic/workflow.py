from typing import List, TypedDict

import re
import os
import glob

import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from prophet import Prophet

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph

from agentic.tools import run_sql_pl

SYSTEM_PROMPT = """
You are a senior data analyst working with GitHub repository statistics
stored in a PostgreSQL database.

You have access to a helper function:

    from agentic.tools import run_sql_pl
    df = run_sql_pl("<SQL query>")

which returns a Polars DataFrame for a given SQL query.

IMPORTANT DATAFRAME RULES (CRITICAL):

1. `run_sql_pl` returns a **Polars DataFrame**.
2. Immediately after **every** call to `run_sql_pl`, you MUST convert it
   to a Pandas DataFrame:

       df = run_sql_pl(...)
       df = df.to_pandas()

3. After that, do **all further processing in Pandas**, not Polars:
   - Do NOT use `pl.col`, `df.with_columns`, or other Polars Expr APIs.
   - You MAY use `.apply`, `.map`, `.pivot_table`, etc. on the Pandas DataFrame.

Example pattern:

    df = run_sql_pl(\"\"\"SELECT ...\"\"\")
    df = df.to_pandas()
    df["my_col"] = df["my_col"].astype(int)
    pivot = df.pivot_table(...)
    answer_str = pivot.to_markdown()

The database contains:

- repos(full_name, owner, name, stars, forks, open_issues, watchers, fetched_at)
- issues(id, repo_full_name, number, state, created_at, closed_at, is_pull_request)
- pulls(id, repo_full_name, number, state, created_at, closed_at, merged_at)
- commits(id, repo_full_name, sha, committed_at)

When the user asks a question, you MUST:

1. Respond ONLY with a single Python code block, fenced with ```python ... ```.
2. Inside the code:
   - import polars as pl
   - import pandas as pd
   - import matplotlib.pyplot as plt
   - from prophet import Prophet
   - import statsmodels.api as sm
   - from agentic.tools import run_sql_pl
3. Use run_sql_pl() for all SQL queries.
4. You can write any additional helper functions inside the code, but:
   - Do NOT include plain-English headings like "Query to get ..." as bare
     statements. Only valid Python is allowed.
   - Comments starting with "#" are allowed, but do not write markdown headings.
5. For text/table answers:
   - build the final explanation or markdown table as a string in a variable named `answer_str`.
6. For chart answers:
   - build a matplotlib chart
   - save it as 'chart.png' using: plt.savefig("chart.png", bbox_inches="tight")
   - NEVER save to any other filename (do NOT use repo names in the filename,
     do NOT save multiple PNG files).
   - also set `answer_str` to a short explanation of the chart.
   - Do NOT produce horizontal bar charts.
   - Do NOT rotate axes or flip coordinates.
   - Bar charts must be standard vertical bars only.
7. DO NOT call plt.show().
8. The LAST line of the script MUST be exactly:
   answer_str
   (so that evaluating the script returns the value of answer_str).
9. When using statsmodels (e.g., ExponentialSmoothing or ARIMA) for
   forecasting, you MUST first check how many data points you have for
   each time series. Only use a seasonal component if there are at least
   2 * seasonal_periods observations. Otherwise, fit a **non-seasonal**
   model (no seasonal argument) or fall back to a simple trend-only
   model. Never let the code crash due to too few data points.
"""

class AgentState(TypedDict):
    question: str
    messages: List
    result: str


def _extract_code_block(text: str) -> str:
    """
    Extract Python code from a ```python ... ``` or ``` ... ``` block.
    If none found, return the raw text.
    """
    # ```python ... ```
    m = re.search(r"```python(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # plain ``` ... ```
    m = re.search(r"```(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()

    return text.strip()


def _run_code_in_repl(code: str) -> str:
    """
    Execute the generated Python code in a controlled namespace that
    has pl, pd, plt, sm, Prophet, and run_sql_pl available.

    Returns the string value of answer_str if present, otherwise any
    printed output, or an error message including the generated code.
    """
    ns = {
        "pl": pl,
        "pd": pd,
        "plt": plt,
        "sm": sm,
        "Prophet": Prophet,
        "run_sql_pl": run_sql_pl,
    }

    try:
        exec(code, ns)

        # --- NEW: ensure there is a chart.png for the UI to display ---
        try:
            if not os.path.exists("chart.png"):
                pngs = [f for f in glob.glob("*.png") if not f.startswith("._")]
                if pngs:
                    latest = max(pngs, key=os.path.getmtime)
                    if latest != "chart.png":
                        # copy or rename the most recent plot to chart.png
                        from shutil import copyfile
                        copyfile(latest, "chart.png")
        except Exception:
            # If anything goes wrong here, just ignore – it's a best-effort step
            pass
        # -----------------------------------------------------------------

        if "answer_str" in ns and ns["answer_str"] is not None:
            return str(ns["answer_str"])

        return "Code executed successfully, but no `answer_str` was set."
    except Exception as e:
        return (
            f"Error while executing generated code: {e}\n\n"
            f"Generated code was:\n\n{code}"
        )



def build_graph():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def run_node(state: AgentState) -> AgentState:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=state["question"]),
        ]
        response = llm.invoke(messages)
        raw_text = response.content if isinstance(response.content, str) else str(response.content)

        code = _extract_code_block(raw_text)
        result_text = _run_code_in_repl(code)

        # Keep messages around for debugging / future extensions
        messages.append(response)
        return {
            "question": state["question"],
            "messages": messages,
            "result": result_text,
        }

    graph = StateGraph(AgentState)
    graph.add_node("run", run_node)
    graph.add_edge(START, "run")
    graph.add_edge("run", END)

    return graph.compile()
