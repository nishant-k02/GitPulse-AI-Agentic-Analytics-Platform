from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from src.config import PG_DSN

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(PG_DSN, echo=False, future=True)
    return _engine


def init_db() -> None:
    """Create tables from schema.sql."""
    from pathlib import Path

    engine = get_engine()
    schema_path = Path(__file__).with_name("schema.sql")
    with engine.begin() as conn, open(schema_path, "r", encoding="utf-8") as f:
        conn.execute(text(f.read()))
