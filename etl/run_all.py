from .fetch_stocks import run as stocks
from .fetch_bls import run as bls
from .fetch_usaspending import run as budgets
from .build_site_data import run as build

if __name__ == "__main__":
    # Each fetch function is idempotent and uses INSERT OR IGNORE to avoid dupes
    stocks()
    bls()
    budgets()
    build()
    print("ETL complete. JSON exported to site/data/")
