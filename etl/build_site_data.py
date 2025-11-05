import json
from pathlib import Path
from sqlalchemy import text
from datetime import datetime, timezone
from .db import engine

ROOT = Path(__file__).resolve().parents[1]
SITE_DATA = ROOT / "site" / "data"
SITE_DATA.mkdir(parents=True, exist_ok=True)

def _wk_pct(seq):
    if len(seq) < 2: return None
    latest = seq[-1][1]
    prev = seq[-6][1] if len(seq) >= 6 else seq[0][1]
    if prev == 0: return None
    return (latest - prev) / prev * 100.0

def run():
    eng = engine()
    with eng.begin() as conn:
        rows = conn.execute(text("SELECT id,name,ticker,sector FROM contractors ORDER BY name")).mappings().all()
        contractors = [dict(r) for r in rows]
        (SITE_DATA / "contractors.json").write_text(json.dumps(contractors, indent=2))

        rows = conn.execute(text("""
            SELECT c.name, c.ticker, c.sector, sp.date, sp.close
            FROM stock_prices sp
            JOIN contractors c ON c.id = sp.contractor_id
            ORDER BY c.name, sp.date
        """)).mappings().all()
        stocks = [dict(r) for r in rows]
        (SITE_DATA / "stocks_timeseries.json").write_text(json.dumps(stocks, indent=2))

        rows = conn.execute(text("SELECT series_id, date, value FROM workforce ORDER BY date")).mappings().all()
        workforce = [dict(r) for r in rows]
        (SITE_DATA / "workforce_timeseries.json").write_text(json.dumps(workforce, indent=2))

        rows = conn.execute(text("""
            SELECT toptier_code, agency_name, fiscal_year, outlay_amount, obligated_amount
            FROM agency_budgets
            ORDER BY agency_name, fiscal_year
        """)).mappings().all()
        budgets = [dict(r) for r in rows]
        (SITE_DATA / "budgets_by_year.json").write_text(json.dumps(budgets, indent=2))

        # metadata
        from collections import defaultdict
        seqs = defaultdict(list)
        for r in stocks:
            if r.get("close") is None: continue
            seqs[r["ticker"]].append((r["date"], float(r["close"])))
        for t in seqs: seqs[t].sort(key=lambda x: x[0])

        stock_weekly = []
        for t, seq in seqs.items():
            name = next((s["name"] for s in stocks if s["ticker"] == t), t)
            sector = next((s["sector"] for s in stocks if s["ticker"] == t), None)
            pct = _wk_pct(seq)
            stock_weekly.append({"ticker": t, "name": name, "sector": sector, "pct_change": pct if pct is not None else 0.0})
        stock_weekly.sort(key=lambda x: abs(x["pct_change"]), reverse=True)

        non_index = [s for s in stock_weekly if (s.get("sector") or "").lower() != "index"]
        avg_stocks = sum(s["pct_change"] for s in non_index)/len(non_index) if non_index else 0.0
        def badge(v): return "Good" if v > 1 else "Bad" if v < -1 else "Same"

        meta = {
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "trends": {
                "stocks": badge(avg_stocks),
                "budgets": "Same",
                "workforce": "Same"
            },
            "stock_weekly": stock_weekly
        }
        (SITE_DATA / "metadata.json").write_text(json.dumps(meta, indent=2))

if __name__ == "__main__":
    run()
