# Output — Europress × Since AI 2026, customer-dashboard track

| File | What |
|---|---|
| `01_transcript_analysis.md` | What Europress told us (Finnish part translated + our English Q&A), mapped to our notes |
| `02_dashboard.md` | The dashboard: features, demo customer numbers, every formula, AI advisor, design, limits |
| `03_deployment.md` | How it runs on this machine at http://hackathon.tail8f13e3.ts.net:8080 (tailnet now; europress.acq.ee later) |
| `04_business_findings_and_decisions.md` | **All business findings and decisions**: company facts, market, data evidence, product scope, pricing (incl. the €8 vs €12–15 decision), economics, go-to-market, operator stance, risks, KPIs, decision log (25 entries), open questions |
| `04_business_findings_explained.md` | **Plain-language version of 04** for readers without background: same findings and decisions, with a glossary, the one-minute story and every term explained |
| `05_business_plan_addon.md` / `.html` | **Complete business plan + dashboard add-on** (after the second Europress session): 7 modules (weight engine, five-answer home, sales briefs, operator feed, map & weather, quality, reporting), integration into the 3 workspaces with live mockups (map, real FMI/ERA5 weather, 3D weight lab), market comparison, pricing, financials, Phase 0 budget, partners, communication plan, roadmap with gates, risks, questions. Published: https://claude.ai/artifact/MeVR2iDqkQvdfK25AYEpMp |
| `business_sources/` | Original documents: merged business plan and business case, draft plan (€8 version), weight-track build plan, 12 agent reports (company profile, strategy, CFO/ESG/Poland/data-platform plans, data value, creative ideas, brand, architecture, session comparison) + CFO model script |
| `brand/` | Europress identity captured live: group logo (PNG), SMART logo (SVG), favicons, screenshots of europressgroup.com, epsmart.fi and the SMART portal login |
| `screenshots/` | Every tab (overview FI/EN, savings, machines, contracts, weight, advisor with a live answer, account, operators, FAQ), calculation and contract drawers, account menu, mobile |

Code: `/home/hackathon/europress-dashboard/` (`pipeline/` data build · `server/` Node server · `public/` dashboard · `ai-workspace/` read-only data for the AI).
All data is the synthetic Europress competition pack; prices are hypothetical.
