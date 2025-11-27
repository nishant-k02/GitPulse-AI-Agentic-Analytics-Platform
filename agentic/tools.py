import polars as pl
from langchain_experimental.tools.python.tool import PythonREPLTool
from sqlalchemy import text

from src.db.connection import get_engine

python_repl_tool = PythonREPLTool()  # not used now but fine to keep


def run_sql_pl(query: str) -> pl.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        cols = result.keys()

    if not rows:
        return pl.DataFrame()

    return pl.DataFrame(rows, schema=list(cols))
