import requests
from dateutil.relativedelta import relativedelta
from datetime import date
from sqlalchemy import text
from .db import init_schema

# Series: total government, federal, state, local
SERIES = {
    "CEU9090000001": "Government Total",
    "CEU9091000001": "Federal Government",
    "CEU9092000001": "State Government",
    "CEU9093000001": "Local Government",
}

def run():
    eng = init_schema()
    # pull recent few years
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    for sid in SERIES.keys():
        resp = requests.get(url + sid, timeout=30)
        resp.raise_for_status()
        series = resp.json()["Results"]["series"][0]["data"]
        with eng.begin() as conn:
            for entry in series:
                if entry["period"] == "M13":
                    continue
                # Convert "January" -> "01"
                month_map = {m:i for i,m in enumerate(
                    ["January","February","March","April","May","June","July","August","September","October","November","December"], start=1)}
                month = month_map[entry["periodName"]]
                d = f"{entry['year']}-{month:02d}-01"
                conn.execute(
                    text("""
                    INSERT OR IGNORE INTO workforce (series_id, date, value)
                    VALUES (:sid, :date, :value)
                    """),
                    {"sid": sid, "date": d, "value": float(entry["value"])},
                )

if __name__ == "__main__":
    run()
