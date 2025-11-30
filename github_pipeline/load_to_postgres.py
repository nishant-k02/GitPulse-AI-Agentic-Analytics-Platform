from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db.connection import get_engine, init_db

RAW_DIR = Path(__file__).parents[1] / "data" / "raw"


def load_table(df: pd.DataFrame, table: str):
    engine = get_engine()
    with engine.begin() as conn:
        df.to_sql(table, con=conn, if_exists="append", index=False)


def main():
    init_db()

    repos = pd.read_csv(RAW_DIR / "repos.csv")
    issues = pd.read_csv(RAW_DIR / "issues.csv")
    pulls = pd.read_csv(RAW_DIR / "pulls.csv")
    commits = pd.read_csv(RAW_DIR / "commits.csv")

    # Remove PRs from issues table
    issues = issues[issues["is_pull_request"] == False]  # noqa: E712

    load_table(repos, "repos")
    load_table(issues, "issues")
    load_table(pulls, "pulls")
    load_table(commits, "commits")

    print("Loaded all tables into Postgres.")


if __name__ == "__main__":
    main()
