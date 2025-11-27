from typing import List, TypedDict

import re

import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from prophet import Prophet

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph

from src.agentic.tools import run_sql_pl

SYSTEM_PROMPT = """
You are a senior data analyst working with GitHub repository statistics
stored in a PostgreSQL database.

You have access to a helper function:

    from src.agentic.tools import run_sql_pl
    df = run_sql_pl("<SQL query>")

which returns a Polars DataFrame for a given SQL query.

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
   - from src.agentic.tools import run_sql_pl
3. Use run_sql_pl() for all SQL queries.
4. For text/table answers:
   - build the final explanation or markdown table as a string in a variable named `answer_str`.
5. For chart answers:
   - build a matplotlib chart
   - save it as 'chart.png' using: plt.savefig("chart.png", bbox_inches="tight")
   - also set `answer_str` to a short explanation of the chart.
6. DO NOT call plt.show().
7. The LAST line of the script MUST be exactly:
   answer_str
   (so that evaluating the script returns the value of answer_str).
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
    printed output, or an error message.
    """
    # Namespace with our tools & libs
    ns = {
        "pl": pl,
        "pd": pd,
        "plt": plt,
        "sm": sm,
        "Prophet": Prophet,
        "run_sql_pl": run_sql_pl,
    }

    try:
        # We'll capture the value of answer_str after exec
        exec(code, ns)

        if "answer_str" in ns and ns["answer_str"] is not None:
            return str(ns["answer_str"])

        return "Code executed successfully, but no `answer_str` was set."
    except Exception as e:
        return f"Error while executing generated code: {e}"


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
