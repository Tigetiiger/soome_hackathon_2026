# Output — Europress × Since AI 2026, customer-dashboard track

| File | What |
|---|---|
| `01_transcript_analysis.md` | What Europress told us (Finnish part translated + our English Q&A), mapped to our notes |
| `02_dashboard.md` | The dashboard: features, demo customer numbers, every formula, AI advisor, design, limits |
| `03_deployment.md` | How it runs on this machine at http://hackathon.tail8f13e3.ts.net:8080 (tailnet now; europress.acq.ee later) |
| **Business model** | `simulator-weather-and-stuff/site/business.html` (live: http://100.87.158.27:8765/business.html): the one business model — problem, weight model, customer / partner / Europress sides, how the money is made (a share of predicted savings, Free vs SMART), scenarios, trust and control. The earlier business plans (04/05/06, NUMBERS, business_sources) were deleted on 7 Nov 2026 because they contradicted it |
| `submission/` | **Grading map + required submission items** (Challenge Brief §06–07): criteria → evidence, deliverables checklist with open TODOs, `THIRD_PARTY_LICENSES.md` + `third_party_inventory.csv` (every library/model/dataset/service, licence, commercial restrictions), `ASSUMPTIONS_AND_UNTESTED.md` |
| `brand/` | Europress identity captured live: group logo (PNG), SMART logo (SVG), favicons, screenshots of europressgroup.com, epsmart.fi and the SMART portal login |
| `screenshots/` | Every tab (overview FI/EN, savings, machines, contracts, weight, advisor with a live answer, account, operators, FAQ), calculation and contract drawers, account menu, mobile |

Code: `/home/hackathon/europress-dashboard/` (`pipeline/` data build · `server/` Node server · `public/` dashboard · `ai-workspace/` read-only data for the AI).
All data is the synthetic Europress competition pack; prices are hypothetical.
