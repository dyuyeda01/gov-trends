import datetime as dt
import yfinance as yf
from sqlalchemy import text
from .db import init_schema

CONTRACTORS = [
    {"name": "Leidos", "ticker": "LDOS", "sector": "Defense/Cyber"},
    {"name": "SAIC", "ticker": "SAIC", "sector": "Defense/IT"},
    {"name": "Booz Allen Hamilton", "ticker": "BAH", "sector": "Consulting/Defense"},
    {"name": "RTX", "ticker": "RTX", "sector": "Defense"},
    {"name": "Lockheed Martin", "ticker": "LMT", "sector": "Defense"},
    {"name": "Northrop Grumman", "ticker": "NOC", "sector": "Defense"},
    {"name": "General Dynamics", "ticker": "GD", "sector": "Defense"},
]

def run():
    eng = init_schema()
    # ensure contractors
    with eng.begin() as conn:
        for c in CONTRACTORS:
            conn.execute(
                text("""INSERT OR IGNORE INTO contractors (name, ticker, sector)
                        VALUES (:name, :ticker, :sector)"""),
                c,
            )

    end = dt.date.today()
    start = end - dt.timedelta(days=120)

    with eng.begin() as conn:
        for c in CONTRACTORS:
            hist = yf.Ticker(c["ticker"]).history(start=start, end=end)
            # map contractor_id
            cid_row = conn.execute(
                text("SELECT id FROM contractors WHERE ticker=:t"), {"t": c["ticker"]}
            ).first()
            if not cid_row:
                continue
            (cid,) = cid_row
            for idx, row in hist.iterrows():
                payload = {
                    "contractor_id": cid,
                    "date": idx.date().isoformat(),
                    "open": float(row["Open"]),
                    "close": float(row["Close"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "volume": float(row["Volume"]),
                }
                conn.execute(
                    text("""
                    INSERT OR IGNORE INTO stock_prices
                    (contractor_id, date, open, close, high, low, volume)
                    VALUES (:contractor_id, :date, :open, :close, :high, :low, :volume)
                    """),
                    payload,
                )

if __name__ == "__main__":
    run()
