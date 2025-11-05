"""
fetch_budgets.py — Pulls top agency budgets from USAspending.gov
"""

import requests
from sqlalchemy import create_engine

DB_PATH = "data/govtrends.db"

def run():
    print("Fetching top agencies from USAspending.gov ...")
    url = "https://api.usaspending.gov/api/v2/agency/"
    resp = requests.get(url)
    if resp.status_code != 200:
        print("Error fetching agency list:", resp.status_code)
        return

    data = resp.json().get("results", [])
    records = []
    for d in data:
        records.append((
            d.get("toptier_code"),
            d.get("agency_name"),
            d.get("outlay_amount") or 0.0,
            d.get("obligated_amount") or 0.0,
            d.get("current_total_budget_authority_amount") or 0.0,
            2025  # approximate current fiscal year
        ))

    eng = create_engine(f"sqlite:///{DB_PATH}")
    with eng.begin() as conn:
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS agency_budgets (
            id INTEGER PRIMARY KEY,
            toptier_code TEXT,
            agency_name TEXT,
            fiscal_year INTEGER,
            outlay_amount REAL,
            obligated_amount REAL,
            UNIQUE(toptier_code, fiscal_year)
        );
        """)
        conn.executemany(
            "INSERT OR REPLACE INTO agency_budgets (toptier_code, agency_name, fiscal_year, outlay_amount, obligated_amount) VALUES (?, ?, ?, ?, ?)",
            [(a,b,fy,o,obl) for (a,b,o,obl,_,fy) in records]
        )

if __name__ == "__main__":
    run()
