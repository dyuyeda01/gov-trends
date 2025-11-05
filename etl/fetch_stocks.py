"""
fetch_stocks.py — Fetches 1 year of daily stock data for major government contractors
and market indices (SPY, NASDAQ). Uses Yahoo Finance public API via yfinance.
"""

import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

DB_PATH = "data/govtrends.db"

CONTRACTORS = [
    {"name": "Leidos", "ticker": "LDOS", "sector": "Defense/Cyber"},
    {"name": "Booz Allen Hamilton", "ticker": "BAH", "sector": "Defense/Cyber"},
    {"name": "Raytheon Technologies", "ticker": "RTX", "sector": "Defense/Cyber"},
    {"name": "SAIC", "ticker": "SAIC", "sector": "Defense/Cyber"},
    {"name": "Lockheed Martin", "ticker": "LMT", "sector": "Defense/Cyber"},
    {"name": "Northrop Grumman", "ticker": "NOC", "sector": "Defense/Cyber"},
    {"name": "General Dynamics", "ticker": "GD", "sector": "Defense/Cyber"},
    {"name": "SPDR S&P 500 ETF", "ticker": "SPY", "sector": "Index"},
    {"name": "NASDAQ Composite", "ticker": "^IXIC", "sector": "Index"},
]


def run():
    print("=== Fetching stock data ===")
    eng = create_engine(f"sqlite:///{DB_PATH}")

    # --- Create tables ---
    with eng.begin() as conn:
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS contractors (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            ticker TEXT UNIQUE,
            sector TEXT
        )
        """)

        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY,
            contractor_id INTEGER,
            date TEXT,
            open REAL,
            close REAL,
            high REAL,
            low REAL,
            volume REAL,
            UNIQUE(contractor_id, date)
        )
        """)

        # Insert contractors
        for c in CONTRACTORS:
            conn.exec_driver_sql(
                "INSERT OR IGNORE INTO contractors (name, ticker, sector) VALUES (?, ?, ?)",
                (c["name"], c["ticker"], c["sector"])
            )

    start = datetime.now() - timedelta(days=365)
    end = datetime.now()

    with eng.begin() as conn:
        contractors = conn.execute(text("SELECT id, name, ticker FROM contractors")).fetchall()

        for contractor_id, name, ticker in contractors:
            print(f"Fetching {ticker}...")
            try:
                df = yf.download(ticker, start=start, end=end, progress=False)
                if df.empty:
                    print(f"⚠️ No data for {ticker}")
                    continue

                # Normalize DataFrame
                df = df.reset_index()
                df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
                df["contractor_id"] = contractor_id
                df.rename(columns={
                    "Date": "date",
                    "Open": "open",
                    "Close": "close",
                    "High": "high",
                    "Low": "low",
                    "Volume": "volume"
                }, inplace=True)
                df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

                # --- Deduplicate (avoid UNIQUE constraint errors) ---
                existing_dates = pd.read_sql(
                    text("SELECT date FROM stock_prices WHERE contractor_id = :cid"),
                    conn, params={"cid": contractor_id}
                )["date"].tolist()

                df = df[~df["date"].isin(existing_dates)]

                if df.empty:
                    print(f"ℹ️ No new rows for {ticker}")
                    continue

                df[["contractor_id", "date", "open", "close", "high", "low", "volume"]].to_sql(
                    "stock_prices", conn, if_exists="append", index=False, method="multi"
                )

            except Exception as e:
                print(f"Error fetching {ticker}: {e}")

    print("✅ Stock data fetch complete.")


if __name__ == "__main__":
    run()
