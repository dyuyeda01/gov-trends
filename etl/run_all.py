"""
run_all.py — master orchestrator to run all ETL tasks
"""

from etl import fetch_stocks, fetch_bls, fetch_usaspending, build_site_data

if __name__ == "__main__":
    print("=== Fetching stock data ===")
    fetch_stocks.run()

    print("=== Fetching workforce data ===")
    fetch_bls.run()

    print("=== Fetching budget data ===")
    fetch_usaspending.run()

    print("=== Building site JSON files ===")
    build_site_data.run()

    print("✅ ETL complete. Data exported to /site/data/")
