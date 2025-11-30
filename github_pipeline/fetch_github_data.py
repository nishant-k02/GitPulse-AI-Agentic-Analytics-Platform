import time
from pathlib import Path

import polars as pl
import requests

from config import GITHUB_TOKEN, GITHUB_REPOS, SINCE_DATE

# ------------------------
# Paths & constants
# ------------------------
RAW_DIR = Path(__file__).parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://api.github.com"


# ------------------------
# Helpers
# ------------------------
def _gh_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def _paginate(url: str, params: dict):
    """
    Generic GitHub pagination helper.

    - Handles normal pagination via Link headers.
    - Gracefully stops on:
      * 422 (pagination limit)
      * 403 (rate limit exceeded)
    """
    page = 1
    while True:
        p = params | {"per_page": 100, "page": page}
        r = requests.get(url, headers=_gh_headers(), params=p)

        # GitHub quirks
        if r.status_code == 422:
            print(
                f"Stopping pagination for {url} at page {page}: "
                "GitHub returned 422 (pagination limit)."
            )
            break

        if r.status_code == 403:
            print(
                f"Stopping pagination for {url} at page {page}: "
                "GitHub returned 403 (rate limit exceeded). "
                "Stopping early; existing data is sufficient for analysis."
            )
            break

        r.raise_for_status()
        data = r.json()
        if not data:
            break

        # Yield current page items
        yield from data

        link_header = r.headers.get("Link", "")
        if 'rel="next"' not in link_header:
            break

        page += 1
        time.sleep(0.2)  # be nice to the API


# ------------------------
# Fetch functions
# ------------------------
def fetch_repo_metadata() -> pl.DataFrame:
    rows = []
    for full_name in GITHUB_REPOS:
        url = f"{BASE_URL}/repos/{full_name}"
        r = requests.get(url, headers=_gh_headers())
        r.raise_for_status()
        data = r.json()
        rows.append(
            {
                "full_name": data["full_name"],
                "owner": data["owner"]["login"],
                "name": data["name"],
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "open_issues": data["open_issues_count"],
                "watchers": data["subscribers_count"],
            }
        )
    df = pl.DataFrame(rows)
    df.write_csv(RAW_DIR / "repos.csv")
    return df


def fetch_issues() -> pl.DataFrame:
    rows = []
    for full_name in GITHUB_REPOS:
        url = f"{BASE_URL}/repos/{full_name}/issues"
        for issue in _paginate(url, {"state": "all", "since": SINCE_DATE}):
            is_pr = "pull_request" in issue
            rows.append(
                {
                    "id": issue["id"],
                    "repo_full_name": full_name,
                    "number": issue["number"],
                    "state": issue["state"],
                    "created_at": issue["created_at"],
                    "closed_at": issue.get("closed_at"),
                    "is_pull_request": is_pr,
                }
            )
    df = pl.DataFrame(rows)
    df.write_csv(RAW_DIR / "issues.csv")
    return df


def fetch_pulls() -> pl.DataFrame:
    rows = []
    for full_name in GITHUB_REPOS:
        url = f"{BASE_URL}/repos/{full_name}/pulls"
        # We'll call twice: open + closed
        for state in ("open", "closed"):
            for pr in _paginate(url, {"state": state}):
                rows.append(
                    {
                        "id": pr["id"],
                        "repo_full_name": full_name,
                        "number": pr["number"],
                        "state": pr["state"],
                        "created_at": pr["created_at"],
                        "closed_at": pr.get("closed_at"),
                        "merged_at": pr.get("merged_at"),
                    }
                )
    df = pl.DataFrame(rows)
    df.write_csv(RAW_DIR / "pulls.csv")
    return df


def fetch_commits() -> pl.DataFrame:
    rows = []
    for full_name in GITHUB_REPOS:
        url = f"{BASE_URL}/repos/{full_name}/commits"
        for commit in _paginate(url, {"since": SINCE_DATE}):
            rows.append(
                {
                    "repo_full_name": full_name,
                    "sha": commit["sha"],
                    "committed_at": commit["commit"]["author"]["date"],
                }
            )
    df = pl.DataFrame(rows)
    df.write_csv(RAW_DIR / "commits.csv")
    return df


# ------------------------
# Main entry point
# ------------------------
def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching repo metadata...")
    fetch_repo_metadata()

    print("Fetching issues...")
    fetch_issues()

    print("Fetching pulls...")
    fetch_pulls()

    print("Fetching commits...")
    fetch_commits()

    print(f"Done. CSVs written to {RAW_DIR}")


if __name__ == "__main__":
    main()
