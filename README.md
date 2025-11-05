# GovTrends AI

**Transparent, daily-updating dashboards** for:
- Contractor stock trends (Leidos, SAIC, BAH, RTX, LMT, NOC, GD)
- Agency budget trends (USAspending)
- Government workforce trends (BLS, optional OPM CSV)

This repository is designed to be hosted on **GitHub Pages** under a subfolder path:
`https://<username>.github.io/gov-trends/`.

## How it works

- **GitHub Actions** runs ETL daily:
  1) Pulls data (yfinance, BLS, USAspending)
  2) Appends to **SQLite** (`data/govtrends.db`)
  3) Exports clean **JSON** into `site/data/`
- **GitHub Pages** serves the static site from `/site` (no backend).

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m etl.run_all   # build db + export JSON
# then open site/index.html in a browser (or serve with: python -m http.server -d site 8000)
```

## Deploy to GitHub Pages

1. Push this repo to GitHub (e.g., `dyuyeda01/gov-trends`).
2. Go to **Settings → Pages**:
   - **Source**: Deploy from branch
   - **Branch**: `main`
   - **Folder**: `/site`
3. Enable GitHub Actions (they run on push and daily).

### Data Sources (free)
- **Stocks:** Yahoo Finance via `yfinance`.
- **Workforce:** BLS public API (no key needed under 500/day).
- **Budgets:** USAspending public API.

## Troubleshooting

- If charts show blank on first load, ensure `site/data/*.json` exists.
  Run `python -m etl.run_all` locally to generate initial JSON,
  or wait for the scheduled GitHub Action to populate data.
- All asset paths are **relative** (`./...`) to support the `/gov-trends/` subfolder.

