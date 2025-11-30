import polars as pl
from sqlalchemy import text

from db.connection import get_engine
from langchain_experimental.tools.python.tool import PythonREPLTool

python_repl_tool = PythonREPLTool()  # fine to keep even if unused


def run_sql_pl(query: str) -> pl.DataFrame:
    """
    Run a SQL query against Postgres and return the result as a Polars DataFrame.
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()

    if not rows:
        return pl.DataFrame()

    # Convert each SQLAlchemy row to a dict of column -> value
    dict_rows = [dict(r._mapping) for r in rows]
    return pl.DataFrame(dict_rows)
