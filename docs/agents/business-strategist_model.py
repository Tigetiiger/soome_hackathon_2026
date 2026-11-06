"""Unit economics + 3-year Europress revenue scenarios for the 'Verified Weight' commercial offer.

Reproduces every number in docs/agents/business-strategist.md sections 4-5.
Run:  python -I -B business-strategist_model.py
Every input below is an [assumption] chosen by the business-strategist agent unless the comment says
[dataset] (taken from the synthetic Since AI dataset via baselines/business_case.py with the realisation
shares in business-strategist.md) or [sourced]. NOTHING here is a Europress price, cost or forecast.
"""
from dataclasses import dataclass

# ---- customer-side value, per device-year, from the synthetic dataset [dataset] ------------------
# baselines/business_case.py customer_value() on data/competition/public (52 customers, 447 devices),
# multiplied by the realisation shares of business-strategist.md section 4.
REALISABLE_EUR_PER_DEVICE_YEAR = {"low": 242, "base": 576, "high": 978}          # [dataset x assumption]
ELIGIBLE_DEVICE_SHARE = {"low": 0.186, "base": 0.349, "high": 0.369}              # [dataset] 3x test at the scenario price

ANNUITY_72M_6PCT = 0.005 / (1 - 1.005 ** -72)   # EUR per EUR financed per month, 6-year lease at 6 % APR [assumption]


@dataclass(frozen=True)
class Scenario:
    name: str
    smart_devices_t0: int            # installed devices on paid SMART tiers today (biggest unknown, ask Tommi)
    new_smart_devices_per_year: int  # new machines sold per year with SMART attached
    arpu_eur_month: float            # Verified Weight add-on price per device-month
    eligible_share: float            # share of installed SMART devices whose customer passes the 3x value test
    adoption_of_eligible: tuple      # cumulative share of eligible installed devices adopting at end of year 1/2/3
    newbuild_take_rate: float        # share of NEW SMART machines ordered with factory weighing + the tier ("weight-included lease")
    retrofit_cost: float             # installed cost per retrofit unit (Europress cost)
    integrated_cost: float           # BOM per factory-fitted unit
    chains: tuple                    # cumulative enterprise (chain) licences at end of year 1/2/3
    chain_licence_eur_year: float
    opex_per_device_month: float
    upsell_retrofit_share: float = 0.9   # share of installed-base upsell units needing a retrofit (rest already have a scale)
    support_per_customer_month: float = 20.0   # [assumption] ~15 min/month at EUR 80/h
    devices_per_customer: float = 8.6          # [dataset] 447 devices / 52 customers
    onboarding_per_customer: float = 600.0     # [assumption] ~7.5 h intake of contracts+invoices at EUR 80/h
    onboarding_per_device: float = 40.0
    retrofit_markup: float = 0.25
    integrated_markup: float = 0.30


SCENARIOS = {
    "low": Scenario("low", 1500, 150, 10, ELIGIBLE_DEVICE_SHARE["low"], (0.05, 0.12, 0.20), 0.15, 900, 300, (0, 1, 2), 10000, 3.0),
    "base": Scenario("base", 2400, 300, 15, ELIGIBLE_DEVICE_SHARE["base"], (0.08, 0.20, 0.35), 0.30, 600, 150, (1, 2, 4), 20000, 2.5),
    "high": Scenario("high", 4000, 600, 25, ELIGIBLE_DEVICE_SHARE["high"], (0.12, 0.30, 0.50), 0.50, 400, 90, (2, 5, 9), 40000, 2.0),
}


def three_year(s: Scenario):
    rows, prev_up, prev_nb = [], 0.0, 0.0
    for y in range(3):
        smart_base = s.smart_devices_t0 + s.new_smart_devices_per_year * (y + 1)
        up_end = s.smart_devices_t0 * s.eligible_share * s.adoption_of_eligible[y]
        nb_end = s.new_smart_devices_per_year * s.newbuild_take_rate * (y + 1)
        end_dev, prev = up_end + nb_end, prev_up + prev_nb
        avg_dev, added_up, added_nb = (prev + end_dev) / 2, up_end - prev_up, nb_end - prev_nb
        added = added_up + added_nb
        retro, integ = added_up * s.upsell_retrofit_share, added_nb + added_up * (1 - s.upsell_retrofit_share)
        saas = avg_dev * s.arpu_eur_month * 12
        hw_rev = retro * s.retrofit_cost * (1 + s.retrofit_markup) + integ * s.integrated_cost * (1 + s.integrated_markup)
        hw_gp = retro * s.retrofit_cost * s.retrofit_markup + integ * s.integrated_cost * s.integrated_markup
        chain = s.chains[y] * s.chain_licence_eur_year
        revenue = saas + hw_rev + chain
        cost_serve = avg_dev * s.opex_per_device_month * 12 + (avg_dev / s.devices_per_customer) * s.support_per_customer_month * 12
        onboarding = (added / s.devices_per_customer) * s.onboarding_per_customer + added * s.onboarding_per_device
        contribution = saas + hw_gp + chain - cost_serve - onboarding     # hardware counted at margin only
        rows.append(dict(year=y + 1, smart_base=smart_base, upsell_devices=up_end, newbuild_devices=nb_end, weight_devices_end=end_dev,
                         saas=saas, hw_revenue=hw_rev, hw_margin=hw_gp, chain=chain, revenue=revenue, cost_to_serve=cost_serve,
                         onboarding=onboarding, contribution=contribution, arr_end=end_dev * s.arpu_eur_month * 12 + s.chains[y] * s.chain_licence_eur_year))
        prev_up, prev_nb = up_end, nb_end
    return rows


def customer_payback(value_year: float, arpu: float, hw_price: float, upfront: bool):
    """Months to pay back, and benefit/cost ratio over the 72-month lease. value_year = realisable EUR/device-year."""
    monthly_net = value_year / 12 - arpu
    lease_uplift = hw_price * ANNUITY_72M_6PCT
    return dict(lease_uplift_month=lease_uplift,
                payback_months_upfront=(hw_price / monthly_net) if monthly_net > 0 else float("inf"),
                benefit_cost_ratio_lease=(value_year / 12) / (arpu + lease_uplift),
                net_month_lease=value_year / 12 - arpu - lease_uplift)


def break_even(s: Scenario, fixed_cost_year: float):
    contrib = s.arpu_eur_month - s.opex_per_device_month - s.support_per_customer_month / s.devices_per_customer
    devices = fixed_cost_year / (contrib * 12)
    y3_base = s.smart_devices_t0 + s.new_smart_devices_per_year * 3
    return dict(contribution_per_device_month=contrib, break_even_devices=devices, share_of_smart_base_y3=devices / y3_base)


if __name__ == "__main__":
    print("annuity factor", round(ANNUITY_72M_6PCT, 5))
    for k, s in SCENARIOS.items():
        print(f"\n=== {k} ===")
        for r in three_year(s):
            print({a: (round(b) if isinstance(b, float) else b) for a, b in r.items()})
        hw_int, hw_ret = s.integrated_cost * (1 + s.integrated_markup), s.retrofit_cost * (1 + s.retrofit_markup)
        v = REALISABLE_EUR_PER_DEVICE_YEAR[k]
        print("customer integrated:", {a: round(b, 2) for a, b in customer_payback(v, s.arpu_eur_month, hw_int, True).items()})
        print("customer retrofit  :", {a: round(b, 2) for a, b in customer_payback(v, s.arpu_eur_month, hw_ret, True).items()})
        for f in (135000, 270000):
            print("break-even for fixed cost", f, {a: round(b, 3) for a, b in break_even(s, f).items()})
