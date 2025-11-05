"""
fetch_bls.py — Fetches U.S. Bureau of Labor Statistics data (e.g., government employment)
and stores it into SQLite.
"""

import requests
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

DB_PATH = "data/govtrends.db"

# Example: Government Employment Series ID
BLS_SERIES = ["CEU9090000001"]  # Total Government Employment

API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
HEADERS = {"Content-Type": "application/json"}


def run():
    print("=== Fetching workforce data ===")
    eng = create_engine(f"sqlite:///{DB_PATH}")

    with eng.begin() as conn:
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS bls_workforce (
            id INTEGER PRIMARY KEY,
            series_id TEXT,
            date TEXT,
            value REAL,
            UNIQUE(series_id, date)
        )
        """)

        for sid in BLS_SERIES:
            print(f"Fetching BLS series {sid}")
            payload = {"seriesid": [sid], "registrationkey": ""}
            res = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
            res.raise_for_status()
            data = res.json()

            series = data["Results"]["series"][0]
            rows = []
            for item in series["data"]:
                date = f"{item['year']}-{int(item['period'][1:]):02d}-01"
                rows.append((sid, date, float(item["value"])))

            for row in rows:
                conn.exec_driver_sql(
                    "INSERT OR REPLACE INTO bls_workforce (series_id, date, value) VALUES (?, ?, ?)",
                    row
                )

    print("✅ Workforce data fetch complete.")


if __name__ == "__main__":
    run()
