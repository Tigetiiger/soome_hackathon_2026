# Business plan: "Proof of Fullness". Free weight for the 85%, and a door into Poland

Tags: **[F]** fact or sourced. **[D]** computed on `data/competition/public` (synthetic data, hypothetical prices). **[E]** estimate. **[A]** assumption for Tommi to confirm. Every euro here is illustrative, not a real saving.

## 1. Problem and customer

- **Who.** SMART reaches only about 15% of customers. Small customers "just want to save money", and "the winning solution is the cheapest". Poland, the key future market, still runs mostly **fixed schedules**: the customer pays for every lift, full or not [F: brief].
- **Where the money is** [D: label window, 272 days]:

| Policy | Devices | Lifts labelled OVER_SERVICING | Value at stake per device-yr | Customer cost per device-yr |
|---|---|---|---|---|
| FIXED_SCHEDULE | 53 | 32% | **€2,347** | €11,943 |
| HYBRID | 42 | 30% | €2,503 | €13,364 |
| ON_CALL | 352 | 6% (other causes) | €395 | €9,553 |

  A fixed-schedule device carries about 6x the unnecessary-lift value of an on-call one. That is about 20% of its bill [D].
- **The simulation agrees** [D: `decision_outcomes`, permissible actions only, fixed-schedule devices]:
  - `SWITCH_TO_ON_CALL` comes out positive in 74% of cases, median +€210 per 56 days (about €1,370/yr).
  - `REDUCE_FREQUENCY` is positive in 99% of cases (n=128).
- **Why customers don't switch.** The operator holds the only weight and earns per transport. The customer cannot prove the container was half empty [F: brief]. One operator (OP-D) shares **0%** of its tickets. Device mass recovers €/t for 909 of the 952 lifts where it would otherwise be unknown [D: `analysis/outputs/03_summary.json`].

**Poland specifics** [F, from secondary and law-firm sources found by web search; not primary statutes]:
- **Commercial vs municipal.** Business-activity waste is largely outside the municipal (gmina) system, and firms contract private haulers. Some gmina tenders do include non-residential properties ([great.gov.uk tender](https://www.great.gov.uk/export-opportunities/opportunities/waste-services-15931), [FCC Polska](https://www.fcc-group.eu/polska/fcc-oferta-odbior-odpadow/business-services)).
- **Contracts.** They are priced per container emptying, sometimes per Mg. They carry a separate **harmonogram** (schedule) annex, settle monthly, and run for one year or with one month's notice ([gov.pl tender](https://www.gov.pl/web/sprawiedliwosc/rozeznanie-rynku-w-zakresie-odbioru-odpadow-komunalnych-zbieranych-selektywnie-z-nieruchomosci-ministerstwa-sprawiedliwosci), [posir.poznan.pl](https://posir.poznan.pl/wp-content/uploads/2018/03/MA.404.7.2018-1.pdf)). This is exactly the fixed-schedule pattern.
- **BDO register.** Every waste transfer needs an electronic transfer card (KPO) in BDO that records waste **mass**, and errors carry penalties ([dudkowiak.com](https://www.dudkowiak.com/environmental-law-in-poland/bdo-register-in-poland/), [Rödl & Partner](https://www.roedl.pl/en/good-to-know/good-to-know/law-and-tax-news/the-bdo-register-all-about-obligations-and-penalties)).
- **Market structure.** The market is fragmented. Remondis holds about 10% of household collection, PreZero and Alba are also active, and about 40% of firms are municipal ([GTAI](https://www.gtai.de/de/trade/polen/branchen/branchenstruktur-1072340)).
- **Cost pressure.** The landfill-fee upper rate is 418.03 zł/Mg in 2025 ([Monitor Polski 2024 poz. 794](https://eli.gov.pl/eli/MP/2024/794/ogl/pol/pdf)). EPR reform is under way, and the EU PPWR applies from 12 Aug 2026 ([certivo](https://www.certivo.com/blog-details/poland-packaging-epr-compliance-2026-bdo-registration-and-annual-reporting)).
- **Material value is low.** Loose cardboard fetches about 0.23 zł/kg and baled about 505 zł/t ([kb.pl](https://kb.pl/porady/cena-makulatury-aktualny-cennik-skupu-makulatury-w-calej-polsce/), an undated aggregator). So **avoided lifts, not material credits, are the lever**.

## 2. Value proposition

**"Stop paying to move air. Your compactor proves how full it was, for free."**

- **What is measured.** Every pickup is stamped with fill % and a **virtual-scale kg** (pressure-based, no extra hardware, ±7–12% [E: weighing-engineer §0]).
- **What the customer sees.** A monthly one-pager, for example: "12 lifts paid; 5 under 40% full, 0.9 t vs 3 t capacity". It ends with a one-click, human-approved **schedule-change request**: one step down the ladder (5/3/2/1/0.5/0.25 lifts/week), then an on-call trial.

**Customer benefit** [D + A]:
- At 40% realisation of the €2,347 stake, a fixed-schedule device saves **about €940/yr**. Realisation is limited by hygiene rules, operator acceptance and contract notice.
- This matches the team's dev best-set figure (≈€1,064 per contract-year on €13.5k cost).
- At half the price level (Poland [A]) the saving is about €470/yr.

**Weight vs fill, honestly** [D: `04_lift_rules.csv`]:
- For *detecting* over-servicing, fill below 40% and mass-implied fill perform the same: recall about 0.91, precision about 0.44.
- Weight still earns its place three ways:
  - **Kg is evidence that operators accept**; a fill percentage is not.
  - It gives €/t even when no tickets are shared.
  - It catches false-high fill sensors: 96% of S40 lifts, against 47% for fill alone.

## 3. Product and tiers

| Tier (SMART) | Customer gets | Price | Cost to Europress |
|---|---|---|---|
| **Weight Free** (Intro, default in every new lease or service contract) | kg + fill per pickup; monthly Proof-of-Fullness PDF; schedule-fit score; mass-log export for **BDO/KPO cross-check** (PL) | **€0** | about €15/device-yr for cloud, e-mail and amortised support [E]; one-off OTA firmware engineering [A] |
| **Pay-from-Savings** (Insights) | Free tier plus drafted schedule-change letter (human approval), on-call trial using SMART fill triggers, verified avoided-lift ledger | **25% of verified avoided-lift cost**, capped at €30/device-month; €0 if no saving | about €40/device-yr [E] |
| **Verified** (Integrated) | Plus invoice-vs-device reconciliation within tolerance, €/t per stream, operator data handshake, optional load-cell platform | €19–29/device-month, or bundled into a premium lease [A] | load-cell option ≈€1.0–1.9k BOM [E: weighing lens] |

**Verified-saving rule (auditable):**
- Saving = (lifts in the old harmonogram − actual lifts) × lift price.
- Any emergency, side-waste or overflow fees are subtracted. This avoids the dataset's `hidden_cost_trap`.
- The calculation uses the dataset's `economics.py` rules [F: ECONOMIC_MODEL §3, §6]. The customer approves the baseline at signup.

**Onboarding** needs no site visit:
1. Europress activates the virtual scale over the air.
2. The customer enters (or photographs) the lift price and schedule.
3. The first report arrives after 30 days [E].

## 4. Pricing sensitivity

Per fixed-schedule device-year, on the €2,347 gross stake [D]:

| Price level | Realisation | Customer value | Europress at 20% share | at 25% | at 30% |
|---|---|---|---|---|---|
| FI (dataset) | 20% | €469 | €94 | €117 | €141 |
| FI | **40%** | **€939** | €188 | **€235** | €282 |
| FI | 60% | €1,408 | €282 | €352 | €422 |
| PL (×0.5) [A] | 20% | €235 | €47 | €59 | €70 |
| PL | 40% | €469 | €94 | €117 | €141 |
| PL | 60% | €704 | €141 | €176 | €211 |

- **For the customer:** they keep 70–80% of the saving and risk nothing upfront.
- **For Europress, the free tier's cost:** about €15/device-yr is recovered by one paid conversion per roughly 8 (FI) to 16 (PL) free devices.

## 5. Revenue model

1. **Gain-share.** This is the main line. It is self-funding because it is billed only out of a verified saving.
2. **Flat fee** for Verified customers.
3. **Strategic pull-through.** This is the real prize, and it is not counted below:
   - In Poland, the report makes lease sales concrete: "this machine pays its lease in avoided lifts".
   - Free weight raises service-contract retention.
4. **Out of scope:** trucks, transport brokerage and material trading [F: Tommi's red lines].

## 6. Three-year illustrative numbers (software line only) [A]

Inputs by scenario:

| | Low | Base | High |
|---|---|---|---|
| Paid conversion Y1/Y2/Y3 | 10/15/20% | 15/25/30% | 20/30/40% |
| Blended ARPU | €120 | €180 (FI/PL mix) | €240 |
| Fixed team cost per year | €150k | €200k | €250k |

Variable costs in all scenarios: €15 per free device and €25 extra per paid device.

| Scenario | Free devices Y1/Y2/Y3 | Paid devices Y3 | Revenue Y1/Y2/Y3 | Net Y1/Y2/Y3 |
|---|---|---|---|---|
| Low | 800 / 2,000 / 3,500 | 700 | €10k / €36k / €84k | −€154k / −€152k / −€136k |
| **Base** | 1,500 / 4,000 / 7,000 | 2,100 | €41k / €180k / €378k | −€188k / −€105k / **+€21k** |
| High | 2,500 / 6,500 / 11,000 | 4,400 | €120k / €468k / €1,056k | −€180k / +€72k / +€531k |

**Break-even in the base case.** The 3-year cumulative gap is about €270k. That is covered by either of these [A]:
- about **90 extra leases** at €3k contribution each, or
- about 1 pp lower churn on a ~€27M service book.

Tommi must supply installed base, service margin and churn.

## 7. Go-to-market and pilot

- **Pilot (90 days, 40 devices) [A]:**
  - Who: 20 Finnish fixed or hybrid customers (the 30–40% not on call) and 20 Polish customers, recruited via Europress Polska Sp. z o.o., Warsaw ([EMIS](https://www.emis.com/php/company-profile/PL/Europress_Polska_Sp_z_oo_en_2015247.html)) and the Polish factory network.
  - Profile: small retail and logistics sites running mixed and cardboard streams.
  - Success gates:
    - fewer lifts with **zero** overflow or hygiene breaches;
    - device kg within ±10% of the ticket on at least 85% of lifts;
    - at least 50% of operators accept the schedule change;
    - at least 25% of customers opt into the paid tier.
- **Year 1:** Free becomes the default in new FI and PL leases, and Pay-from-Savings is offered to every fixed-schedule device.
- **Years 2–3:** expand to CZ, SK and the Baltics, which have the same pattern [E].
- **Channels:** on-site service technicians, Polish dealers, retail-chain franchisees.
- **Poland hook:** Polish-language report with KPO export.

## 8. Operator-neutral partnerships

- **Operators get a free pickup-request feed** (fill, kg, ETA to full): fewer wasted trips, lower cost per tonne.
- **Per-transport conflict:** advise per-emptying plus per-Mg pricing, or on-call with a minimum-load clause; tendering is never the headline.
- **Root cause before blame.** Every discrepancy is attributed first: sensor, tare, side waste or combined load (team concept C4).
- **BDO.** The mass log is offered to the operator to cross-check KPO mass. Who confirms mass in BDO is unverified [A].

## 9. Risks

| Risk | Mitigation |
|---|---|
| Virtual-scale accuracy is unproven (no pressure data) | A "half empty" claim needs only ±10% [F: red-team §0]. Validate per the weighing lens |
| Operators refuse schedule changes or raise lift prices | Gain-share nets out price changes; operator feed; time the change to contract notice |
| Gmina-run schedules can't be negotiated | Screen these out at onboarding. They still get BDO and €/t value |
| Hygiene or bio-waste maximum intervals | The ladder respects `max_interval_violations`. No auto-suggestions for bio-waste |
| Synthetic data | Every € is labelled illustrative. The pilot is the first real evidence |

## 10. KPIs

Free activations · report open rate ≥60% · lifts per device-month on fixed fleets −25% · overflow incidents not increasing · paid conversion ≥20% by Y2 · verified € avoided per device · free-tier cost ≤€15/device-yr · operator acceptance ≥50% · PL lease win rate with vs without the report.

## 11. Pitch

Eighty-five percent of Europress customers don't buy SMART. In Poland most still pay for every scheduled lift, full or not. In our data a fixed-schedule compactor carries about €2,300 a year of unnecessary-lift value, six times an on-call one (synthetic data, hypothetical prices). We switch on a zero-hardware virtual scale in every lease, free. After each pickup the customer gets proof, in kilograms, of how full the container really was, plus a one-click, human-approved request for a better schedule. Europress charges nothing unless the customer saves, then takes a quarter of the verified saving. The free tier costs about €15 per machine per year. It turns Poland's fixed-schedule market into on-demand SMART customers, and every report sells the next lease.

---

### 3 strongest ideas
1. **Aim at fixed schedules.** They hold €2,347 vs €395 per device-year, and switching to on-call is positive in 74% of simulations. This is exactly the Polish market.
2. **Free weight plus gain-share.** It is self-funding and carries no risk for the customer. The verified-saving rule can be audited with the dataset's own economics engine and avoids the hidden-cost trap.
3. **BDO/KPO mass cross-check.** It gives Polish customers a compliance reason to activate before any saving, and operators find it friendly.

### 3 weakest points
1. **Thin software P&L.** The base case breaks even only in Y3. The real justification is lease pull-through and retention, and we have no numbers for either.
2. **Weight adds little over fill for *detecting* over-servicing** (recall 0.91 either way). Its value is persuasion and €/t, which is hard to quantify.
3. **Key inputs are assumptions.** The Polish price level (×0.5), the 40% realisation and gmina coverage of commercial sites are all assumed. Polish facts are secondary sources.
