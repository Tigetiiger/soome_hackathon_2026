"""Export the numbers for impact.py (v2, business model of 7 Nov 2026) into data/impact_v2.json.

Every value is read from the dashboard data that business.html quotes, so the clip, the app and the
business page agree:
    europress-dashboard/public/data/customers/ORG-0049.json   hero customer: cost, savings, levers
    europress-dashboard/public/data/customers/*.json          52 demo customers: savings sum
    europress-dashboard/public/data/operators/OP-*.json       5 demo partners: trips saved
The 25 % share and the load-cell cost range are stated assumptions (business.html §4 and §7).

    python3 export_impact_v2.py
"""

from __future__ import annotations

import json
from pathlib import Path

DASH = Path("/home/hackathon/europress-dashboard/public/data")
OUT = Path(__file__).resolve().parent / "data" / "impact_v2.json"
FEE_SHARE = 0.25  # demo value; the real share is agreed per customer (business.html §4)
LOADCELL_EUR_PER_MACHINE = (3400, 6300)  # installed, estimate (business.html §7, Table 4)
REFERENCE_MACHINES = 10


def main() -> None:
    hero = json.loads((DASH / "customers" / "ORG-0049.json").read_text())
    kpis = hero["kpis"]
    levers = [{"id": l["id"], "eur": round(l["saving_eur"])} for l in hero["levers"]]
    savings = round(kpis["savings"]["value"])
    if sum(l["eur"] for l in levers) != savings:
        raise SystemExit(f"levers {sum(l['eur'] for l in levers)} != savings {savings}")

    customers = sorted(DASH.glob("customers/ORG-*.json"))
    fleet_savings = sum(json.loads(p.read_text())["kpis"]["savings"]["value"] for p in customers)
    partners = sorted(DASH.glob("operators/OP-*.json"))
    trips = sum(json.loads(p.read_text())["value"]["trips_saved_year"] for p in partners)

    fee = round(savings * FEE_SHARE)
    data = {
        "_built_from": "export_impact_v2.py (dashboard data, 7 Nov 2026)",
        "customer": {
            "name": hero["customer"]["name"],
            "total_cost": round(kpis["total_cost"]["value"]),
            "savings": savings,
            "levers": levers,
            "fee_share": FEE_SHARE,
            "fee": fee,
            "keeps": savings - fee,
        },
        "fleet": {
            "customers": len(customers),
            "savings_eur": round(fleet_savings),
            "partners": len(partners),
            "trips_saved": trips,
            "fee_eur": round(fleet_savings * FEE_SHARE),
        },
        "reference_group": {
            "machines": REFERENCE_MACHINES,
            "loadcell_eur_per_machine": list(LOADCELL_EUR_PER_MACHINE),
            "loadcell_eur_total": [v * REFERENCE_MACHINES for v in LOADCELL_EUR_PER_MACHINE],
        },
    }
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(data, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
