import requests
from sqlalchemy import text
from .db import init_schema

def run():
    eng = init_schema()

    # list agencies
    agencies = requests.get(
        "https://api.usaspending.gov/api/v2/references/toptier_agencies/", timeout=60
    ).json().get("results", [])

    with eng.begin() as conn:
        for ag in agencies:
            code = ag.get("toptier_code")
            name = ag.get("agency_name")
            if not code:
                continue
            # summary endpoint per agency
            detail = requests.get(
                f"https://api.usaspending.gov/api/v2/agency/{code}/", timeout=60
            ).json()

            fy = detail.get("current_fy")
            outlay = detail.get("outlay_amount", 0) or 0
            obligated = detail.get("obligated_amount", 0) or 0

            if fy and name:
                conn.execute(
                    text("""
                    INSERT OR IGNORE INTO agency_budgets
                    (toptier_code, agency_name, fiscal_year, outlay_amount, obligated_amount)
                    VALUES (:code, :name, :fy, :outlay, :ob)
                    """),
                    {
                        "code": code,
                        "name": name,
                        "fy": int(fy),
                        "outlay": float(outlay),
                        "ob": float(obligated),
                    },
                )

if __name__ == "__main__":
    run()
