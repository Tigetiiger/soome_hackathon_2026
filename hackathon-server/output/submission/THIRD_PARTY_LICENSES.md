# Third-party libraries, models, datasets and services

_Europress × Since AI Hackathon 2026. Required by the Challenge Brief §07: "Identify every third-party library, model, dataset or service used, its licence and any relevant commercial-use restrictions."_

Machine-readable version: [`third_party_inventory.csv`](third_party_inventory.csv). Versions are taken from the project virtualenvs and binaries on 2026-11-07.

## Summary: what restricts commercial use

| Item | Restriction | Our action |
|---|---|---|
| **Open-Meteo free API** (ERA5 weather in the mockups) | The free tier is **non-commercial only** | Mockups only. Production uses **FMI open data (CC BY 4.0)** with MET Norway as fallback, or a paid Open-Meteo plan |
| **Since AI / Europress synthetic dataset v1.0.1** | The pack contains **no licence file** | Used for the hackathon only. Ask Since AI / Europress before any reuse after the event |
| **Claude Sonnet** (AI advisor in the dashboard) | Proprietary. Questions and data are sent to Anthropic | Production needs a commercial Anthropic API account and a DPA. The advisor already runs in a read-only sandbox with a $0.50 cap per answer |
| **Tailscale** (demo hosting) | The free Personal plan is meant for personal use | Demo only. Production runs on Caddy + HTTPS at a public domain |
| **Google Fonts / jsDelivr CDN** | Visitor IP addresses go to third parties (GDPR concern in the EU) | Self-host the fonts and plotly.js in production. Chart.js is already self-hosted |
| **Europress / SMART logos** | Europress trademarks | Used only in this Europress challenge submission |
| **Blender** (pitch video only) | GPL-2.0+ applies to scripts we distribute; rendered video is not GPL-bound | Not part of the product |

Everything else is permissive (MIT, BSD, Apache-2.0, PSF, OFL): commercial use is allowed if the copyright and licence notices are kept.

## 1. Software libraries in the product code

| Library | Version | Used in | Licence | Commercial use |
|---|---|---|---|---|
| NumPy | 2.5.4 | all Python projects | BSD-3-Clause | Yes |
| pandas | 3.1.1 | all Python projects | BSD-3-Clause | Yes |
| PyArrow (Apache Arrow) | 26.0.1 | Parquet I/O | Apache-2.0 | Yes (keep NOTICE) |
| PyYAML | 6.0.3 | configs | MIT | Yes |
| Matplotlib | 3.11.2 | report figures | Matplotlib License (PSF-based) | Yes |
| LightGBM | 4.7.0 | hydraulic soft-sensor weight model (`weight_train`, dashboard weight engine) | MIT | Yes |
| scikit-learn | 1.9.1 | baselines, anomaly and density models | BSD-3-Clause | Yes |
| SciPy | 1.18.1 | statistics, fitting | BSD-3-Clause | Yes |
| joblib, threadpoolctl | 1.6.0, 3.8.0 | transitive (scikit-learn) | BSD-3-Clause | Yes |
| DuckDB | 2.0.0 | SQL over Parquet (analysis) | MIT | Yes |
| pypdf | 7.0.0 | reading the brief PDF (tooling) | BSD-3-Clause | Yes |
| pytest | 9.2.0 | tests (dev only) | MIT | Yes |
| Chart.js (+ bundled @kurkle/color) | 4.4.1 | dashboard charts, self-hosted at `public/vendor/` | MIT | Yes |
| plotly.js-dist-min | 2.35.2 | 3D weight-lab mockup (05 add-on page), via jsDelivr | MIT | Yes |

The dashboard server (`europress-dashboard/server/server.mjs`) uses **only Node.js built-ins**. It has no npm dependencies.

## 2. Runtimes and infrastructure

| Component | Version | Licence | Commercial use |
|---|---|---|---|
| Python | 3.13.5 | PSF License 2.0 | Yes |
| Node.js | 26.13.0 | MIT | Yes |
| Caddy (reverse proxy, automatic HTTPS) | 2.8.4 | Apache-2.0 | Yes |
| Let's Encrypt (TLS, via Caddy) | — | Subscriber Agreement, free | Yes |
| Tailscale (demo network) | 1.104.5 | Client BSD-3; service under Tailscale Terms | Paid plan for business use |

## 3. AI models and AI tools

| Model / tool | Where | Licence / terms | Notes |
|---|---|---|---|
| **Claude Sonnet**, called through the Claude Code CLI 2.1.319 (`--model sonnet`) | Dashboard AI advisor (`server.mjs`) | Proprietary; Anthropic Commercial Terms + Usage Policy | Read-only sandbox over the synthetic data; per-answer budget cap; answers must cite data |
| **LightGBM soft-sensor model** | `simulator-weather-and-stuff/weight_train`, dashboard weight engine | Our own model, trained on our own synthetic data | No third-party pretrained weights |
| scikit-learn models (isolation/anomaly, regression baselines) | analysis, virtual_scale | Our own models | No pretrained weights |
| Claude Code (Opus / Sonnet) | Writing code and documents during the hackathon | Anthropic terms; the output belongs to the user | All output reviewed by the team |
| ChatGPT / OpenAI Codex CLI | `input-files/chatgpt-prompt.md`, `~/.codex` | OpenAI terms | **Team to confirm** whether it was used for the submission |

No pretrained third-party ML weights (e.g. time-series foundation models) are used in the delivered code.

## 4. Datasets

| Dataset | Licence | Commercial use | Notes |
|---|---|---|---|
| **Europress SMART Material Value Engine v1.0.1** (Since AI synthetic competition + quickstart pack) | No licence stated in the pack | Unclear: ask the organisers | ~500 fictional compactors × 365 days. Synthetic; no personal data. Supports Part 2 only; it does **not** validate hardware |
| **compactor_sim** hourly telemetry (our own simulator) | Own work | Yes | All invented; not Europress pressure settings |
| **ERA5 reanalysis** (Copernicus / ECMWF) via **Open-Meteo Historical API** | ERA5: Copernicus licence (commercial OK with attribution). Open-Meteo data: CC BY 4.0 | **Open-Meteo free API: non-commercial only** | Mockup weather only |
| FMI open data *(planned production)* | CC BY 4.0 | Yes, with attribution | Simulator already supports FMI CSV replay |
| MET Norway *(planned fallback)* | CC BY 4.0 / NLOD 2.0 | Yes | Requires an identifying User-Agent |
| National Land Survey of Finland maps *(planned)* | CC BY 4.0 | Yes | — |
| Digitransit / OpenStreetMap tiles *(planned)* | ODbL 1.0 (OSM) | Yes | API key, OSM attribution |

## 5. Fonts, design and hosting services

| Item | Licence | Notes |
|---|---|---|
| Geist Mono, Radio Canada Big, Source Serif 4 (Google Fonts) | SIL OFL 1.1 | Self-host in production (GDPR) |
| IBM Plex Sans / Mono (pitch video) | SIL OFL 1.1 | — |
| Figma (design system file `tODJ1f5NDUh2pWYVcB9SXW`) | Figma Terms | The design is our own work |
| claude.ai Artifacts (shared business-plan page) | Anthropic terms | Private by default |
| jsDelivr CDN (plotly.js) | Free public CDN | Self-host in production |

## 6. Pitch-video tooling (not part of the product)

| Tool | Licence |
|---|---|
| Manim Community Edition | MIT |
| ManimGL | MIT |
| PyVista (VTK) | MIT (VTK BSD-3) |
| three.js 0.170 | MIT |
| playwright-core 1.49 | Apache-2.0 |
| Blender (bpy) | GPL-2.0-or-later (rendered output is not GPL-bound) |
| FFmpeg | LGPL-2.1+ / GPL-2.0+ depending on build (H.264 may carry patent licensing) |

## 7. References (cited, not redistributed)

- Finlex, Act 707/2011 on measuring instruments: public legislation. This is our reading; confirm with Tukes.
- Load-cell, strain-gauge and transmitter datasheets and list prices: see `europress_conclusions/smartweight/SOURCES.md` and `_research/hardware_prices.md`.
- Europress / SMART brand assets in `output/brand/`: Europress trademarks.

_Licence names are from each project's published licence. Before shipping commercially, re-check versions and terms; SaaS terms in particular change._
