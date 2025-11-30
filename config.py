import os
from datetime import datetime, timedelta

# --- GitHub repos for last 2 months ---
GITHUB_REPOS = [
    "meta-llama/llama3",
    "ollama/ollama",
    "langchain-ai/langgraph",
    "openai/openai-cookbook",
    "milvus-io/pymilvus",
]

# Last 60 days window
DAYS_BACK = 60
SINCE_DATE = (datetime.utcnow() - timedelta(days=DAYS_BACK)).isoformat() + "Z"

# Environment variables (set these in your shell)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

POSTGRES_DB = os.getenv("BA1_PG_DB", "bonus_db")
POSTGRES_USER = os.getenv("BA1_PG_USER", "bonus_user")
POSTGRES_PASSWORD = os.getenv("BA1_PG_PASSWORD", "bonus_pass")
POSTGRES_HOST = os.getenv("BA1_PG_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("BA1_PG_PORT", "5432"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Convenience DSN
PG_DSN = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
