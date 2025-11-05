import json
from pathlib import Path
from sqlalchemy import text
from .db import engine

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
SITE_DATA.mkdir(parents=True, exist_ok=True)

def run():
    eng = engine()
    with eng.begin() as conn:
        # contractors
        rows = conn.execute(
            text("SELECT id,name,ticker,sector FROM contractors ORDER BY name")
        ).mappings().all()
        (SITE_DATA / "contractors.json").write_text(
            json.dumps([dict(r) for r in rows], indent=2)
        )

        # stocks time series
        rows = conn.execute(text("""
            SELECT c.name, c.ticker, sp.date, sp.close
            FROM stock_prices sp
            JOIN contractors c ON c.id = sp.contractor_id
            ORDER BY c.name, sp.date
        """)).mappings().all()
        (SITE_DATA / "stocks_timeseries.json").write_text(
            json.dumps([dict(r) for r in rows], indent=2)
        )

        # workforce
        rows = conn.execute(
            text("SELECT series_id, date, value FROM workforce ORDER BY date")
        ).mappings().all()
        (SITE_DATA / "workforce_timeseries.json").write_text(
            json.dumps([dict(r) for r in rows], indent=2)
        )

        # budgets
        rows = conn.execute(text("""
            SELECT toptier_code, agency_name, fiscal_year, outlay_amount, obligated_amount
            FROM agency_budgets
            ORDER BY agency_name, fiscal_year
        """)).mappings().all()
        (SITE_DATA / "budgets_by_year.json").write_text(
            json.dumps([dict(r) for r in rows], indent=2)
        )

if __name__ == "__main__":
    run()
