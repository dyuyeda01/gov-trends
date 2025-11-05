from pathlib import Path
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "govtrends.db"

def engine():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    eng = create_engine(f"sqlite:///{DB_PATH}", future=True)
    return eng

def init_schema():
    eng = engine()
    schema_sql = (ROOT / "etl" / "schema.sql").read_text()

    # Split into individual statements by semicolon and execute sequentially
    statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
    with eng.begin() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)
    return eng
