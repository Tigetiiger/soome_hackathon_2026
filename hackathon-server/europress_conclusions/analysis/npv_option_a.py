"""NPV of the weight add-ons with the measured tier scoped out (option a).

Reuses the CFO model in ../agents/bizplan-cfo_model.py unchanged and changes one input:
prem_share = 0. The measured tier is Europress's existing scale platform, sold at its own
price outside this add-on business case.

Why: the CFO model priced a premium measured tier at EUR 49/month on EUR 1,900 of hardware.
The verified load-cell cost is EUR 3.4-6.3k installed (smartweight/BILL_OF_MATERIALS.md), so
that tier would not pay back within a 72-month lease. Scoping it out is the consistent fix.

Run: python3 europress_conclusions/analysis/npv_option_a.py
"""
from pathlib import Path

MODEL = Path(__file__).resolve().parent.parent / "agents" / "bizplan-cfo_model.py"
SCENARIOS = {
    "low": dict(adopt=[0.02, 0.05, 0.09, 0.12, 0.14, 0.15], price=12, churn=0.12, cts=4.5,
                pl=[0, 0, 0, 1000, 1500, 2000], renew_uplift=25),
    "base": {},
    "high": dict(adopt=[0.05, 0.15, 0.28, 0.35, 0.40, 0.42], price=19, churn=0.05, cts=3.0,
                 renew_uplift=110),
}


def load_model():
    """Execute only the model definitions (everything before the scenario printouts)."""
    source = MODEL.read_text().split("low=sc(")[0]
    namespace = {}
    exec(source, namespace)  # trusted local file written by the team
    return namespace["run"], namespace["sc"]


def main():
    run, sc = load_model()
    for label, extra in (("as published", {}), ("option (a): no measured tier", {"prem_share": 0})):
        print(f"== {label}")
        for name, case in SCENARIOS.items():
            _, npv, payback = run(sc(**{**case, **extra}))
            print(f"   {name:5s} 6-year NPV {npv / 1e6:+.2f}M EUR, payback year {payback}")
        _, sub_only, _ = run(sc(**{**extra, "renew_uplift": 0}))
        print(f"   subscription alone (base, no retention uplift) {sub_only / 1e6:+.2f}M EUR")


if __name__ == "__main__":
    main()
