# SOURCES

All web sources were accessed on 2026-11-07 unless stated. Full notes, quotes and more URLs are in
`_research/legal_metrology.md`, `_research/equipment_priorart_literature.md` and `_research/hardware_prices.md`.

**Evidence class** (spec §1 categories):
- **EP** = Europress publicly confirms
- **LIT** = independent technical literature, standard or law
- **VEN** = vendor or manufacturer claim (not independent)
- **PAT** = patent
- **DATA** = synthetic hackathon dataset (measured on synthetic data only)
- **BRIEF** = hackathon brief or Europress briefing transcript

**Source type:** law, standard, specification, marketing, peer-reviewed (PR), preprint, simulation, experimental measurement.

## 1. Hackathon inputs

| # | Source | Type / class | Key finding used |
|---|---|---|---|
| 1 | Challenge brief PDF, `input-files/Europress_SinceAI2026_FINAL/…BUILDER_FINAL (1).pdf` | BRIEF | Part 1 "Get the weight". The dataset "does NOT prove or benchmark weighing hardware". |
| 2 | Briefing transcript, `europress-brefing.txt` | BRIEF / EP | Europress already logs ram pressure curves and uses them to predict fill. Motor 3–5 kW, SIM/4G, tilt, GPS and movement sensors. The platform scale "costs as much as the compactor itself". A model estimate needs "evidence that it's accurate in all cases". Europress has no long-term data on how cardboard volume and density vary by season. |
| 3 | Europress SMART Material Value Engine v1.0.1 (README, ASSUMPTIONS_AND_LIMITATIONS, ECONOMIC_MODEL, configs/assumptions.yaml, raw parquet) | DATA | Claims checked in `results/dataset_checks.json`; see EXECUTIVE_SUMMARY §6. |
| 4 | Earlier team work: `europress_conclusions/BUSINESS_CASE.md`, `BUSINESS_PLAN.md`, `BUILD_PLAN.md`, `soome_hackathon_2026/docs/agents/weighing-engineer.md`, `virtual_scale/config/sensor_sim.yaml` | internal | Prior tier ladder (virtual scale / ticket-calibrated / platform). Its parameter guesses were reused only as tagged assumptions. |

## 2. Europress equipment (EP, manufacturer documents and marketing)

| # | URL | Key finding |
|---|---|---|
| 5 | https://europressgroup.com/wp-content/uploads/2024/04/Europress-Combimax-product-brochure_ENG-1.pdf | CombiMax: 35 t (≈343 kN) press, 5.5/7.5 kW, 10–22 m³, 20 m³ unit 6,990 × 2,500 × 2,730 mm. Lift hooks and rollers are accessories. No pressure, tare or payload published. |
| 6 | https://europressgroup.com/wp-content/uploads/2024/11/Europress_DuoMax_brochure_ENG.pdf | DuoMax: stationary press, detachable 20–35 m³ container, 35/40 t. |
| 7 | https://europressgroup.com/waste-compactor-containers/ | Container weights 2,300 kg (20 m³) to 3,000 kg (32 m³). |
| 8 | https://europressgroup.com/wp-content/uploads/2026/04/Europress_Scale-Solutions_brochure_ENG.pdf ; https://europressgroup.com/scale-solutions/ | Scale platform: 4 corner sensors on a separate full-length platform, "minimum tolerance 2 kg", no class or legal-for-trade claim. Fill-level settings screen ("Working Pressures", "Front Turn Pressure 185 bar") suggests fill is derived from pressure. |
| 9 | https://europressgroup.com/scaletipper-x1/ | Bin tipper scale: 440 kg max, 1.0 kg accuracy. |
| 10 | https://europressgroup.com/wp-content/uploads/2026/04/Europress_SMARTbrochure_ENG.pdf ; https://epsmart.fi/ | SMART tiers; fill prediction from emptying history; pressing force optimised by fill level; more than 10,000 devices (vendor claim). |

## 3. Law, standards and legal metrology (LIT)

| # | URL | Type | Key finding |
|---|---|---|---|
| 11 | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014L0031 | law | NAWI Directive 2014/31/EU: Art. 1(2)(a)–(b) commercial and fee/tariff uses. Class III MPE ±0.5e/1e/1.5e, doubled in service. Modules B+D/F or G. M marking. |
| 12 | https://legislation.gov.uk/eudr/2014/32/annex/VIII/data.htm?view=plain | law | MID MI-006 catchweighers, class Y(a)/Y(b): automatic in-cycle weighing falls here. |
| 13 | https://www.finlex.fi/fi/lainsaadanto/2011/707 | law | Mittauslaitelaki 707/2011 §2–3: weighing for price, fee, credit (*hyvitys*) or compensation is always regulated. No consent exemption for weighing. |
| 14 | https://www.finlex.fi/fi/lainsaadanto/2016/1431 | law | VNa 1431/2016: trade requires class III. |
| 15 | https://www.finlex.fi/fi/lainsaadanto/2014/471 | law | VNa 471/2014: re-verification every 3 years by a Tukes-approved inspection body. |
| 16 | https://www.kiwa.com/fi/fi/palvelutyyppi/kalibrointi-ja-varmennus/mittauslaitteiden-varmennus/ | VEN | Periodic verification €89 + VAT list price (instrument size unclear). |
| 17 | https://tampere.fi/sites/default/files/2024-12/Jatetaksa-1.1.2025-alkaen.pdf | regulator / municipal | Hooklift containers and compactors are weighed and charged by weight (mixed waste €125/t). Unweighed containers use 55 kg/m³. |
| 18 | https://kiertokaari.fi/rusko-waste-management-centre-service-instructions/ | regulator / municipal | Entry and exit weighbridge at the waste centre. |
| 19 | WELMEC Guide 2 (2015) https://www.laumas.com/pub/norme_direttive/METROLOGIA_LEGALE/NAWI/WELMEC_2.0.pdf | standard | Vehicle-mounted NAWI: tilt limits and sensors; waste vehicles §3.1.13.2. |
| 20 | WELMEC 2.10 modular approach https://welmec-upgrade.bs.ptb.de/welmec/documents/guides/2.10/2021/WELMEC_Guide_2.10_issue_1_v2021.pdf | standard | Approved load cells plus approved indicator can be combined into a modular approval. |
| 21 | OIML R51 / R76 / R134 (oiml.org) | standard | R76 = NAWI; R51 = automatic catchweighers (bin lifts); R134 = weigh-in-motion of road vehicles (not applicable). |
| 22 | DK certificate DK0199.408 (Botek B6-KV) https://sik.dk/sites/default/files/2023-03/midmid_dk0199.408_rev1_2014.pdf | standard / certificate (snippet) | Refuse-truck bin-lift catchweigher, R51 Y(a)/Y(b), Max ≤ 3,500 kg. |
| 23 | https://resourcemedia.eco/article/vws-bin-weighing-system-awarded-eu-approval | news / VEN | Enviroweigh type approval; front-end loader certified to 20 kg. |
| 24 | EN 15430-1 | standard | **Not found.** EN 14803 (waste quantity determination) exists. |

## 4. Weighing products and competitors (VEN unless stated)

| # | URL | Key finding |
|---|---|---|
| 25 | https://tamtron.com/en/product/one-power-truck-on-board-scale | Finnish on-board truck scale, "approved for legal for trade", invoicing basis; no class or accuracy published. No hooklift-specific product found. |
| 26 | https://pfreundt.de/en/products/hook-lift-scale | Hooklift scale listed as class III/IIII "eichfähig" (portfolio PDF via snippet). |
| 27 | https://rds.eu/en/product/calibrated-body-weighing-system | Legal-for-trade body weighing on compactor trucks. |
| 28 | https://www.interfaceforce.com/solutions/test-and-measurement/waste-management-container-weighing/ | 4 wireless load cells under container legs; no accuracy or legal-for-trade claim. |
| 29 | https://www.ricelake.com/products/traderoute-hl-series/ | Legal-for-trade (NTEP) hooklift system, USD 18,480 (listed). |
| 30 | WeDi K3 container scale listing (see hardware_prices.md item 11) | 15 t, 4 cells plus indicator, €4,800–5,620 ex VAT (2024 listing); trade approval not stated. |
| 31 | https://www.aanderaa.com/loadtronic-3 | Wheel-loader pressure weighing "typically better than ±1 %" (vendor). |
| 32 | Tamtron container-stacker / straddle-carrier / timber-crane scales (tamtrongroup.com) | 0.5–2 %, about 1 %; timber crane MID type approval (2025). |

## 5. Patents (PAT)

| # | Patent | Key finding |
|---|---|---|
| 33 | US11162834B2 https://patents.google.com/patent/US11162834B2/en | Retrofit guide frame lifts the container rails onto load-cell rollers so the cells carry the **full** weight; sum minus stored tare. |
| 34 | US10564029B2 | Wheel axles as strain-gauge load pins. |
| 35 | US12379240B1 (Canalytics) | Two hydraulic-piston scales at one end; total extrapolated. States that ram pressure and amperage are unreliable because waste types resist differently. |
| 36 | US5299142A (Marathon) | Fullness from stroke count, then pressure; no mass. |
| 37 | US4603625, US4643087 | Locked-ram back-pressure as a fullness indicator. |
| 38 | US11307080B2 (Hiab) | Hooklift weight from main-cylinder pressure integrated over lift angle. |
| 39 | US11320299 | Mass **and centre of mass** of a hooklift platform during the lift (title only). |
| 40 | US20120285750A1 | Lift-arm load cells; up/down differencing; accumulator damping. |
| 41 | US10982415 | Payload from cylinder pressure; notes circuit loss and viscosity errors (snippet). |

Gap: no patent found that estimates compactor *content mass* from ram pressure, position or motor current. A freedom-to-operate search is still needed.

## 6. Literature (LIT)

| # | Source | Type | Key finding |
|---|---|---|---|
| 42 | Radoičić, Jovanović, Arsić (2016), ETRI J. 38(4):787–797, doi:10.4218/etrij.16.0115.0183 | PR, experimental | On-board weighing on a refuse vehicle (rear-axle force, strain). **Only the abstract was read**; accuracy not retrieved. |
| 43 | Werner et al., arXiv:2510.11574 (2025) | preprint, experimental | Excavator payload from cylinder pressure plus IMUs, about 1 % of full scale with a calibrated dynamic model; the quasi-static method is worse. |
| 44 | Voicu et al. (2023), Annals Fac. Eng. Hunedoara 21(3):131–136 https://annals.fih.upt.ro/pdf-full/2023/ANNALS-2023-3-19.pdf | PR (regional), experimental | Cardboard force–stroke curve "does not follow a predetermined trajectory"; loose infeed about 58–60 kg/m³. |
| 45 | US EPA Standard Volume-to-Weight Conversion Factors (2006) https://19january2021snapshot.epa.gov/sites/static/files/2016-03/documents/conversions.pdf | technical report | OCC loose 59, compacted 237, baled 653 kg/m³. |
| 46 | WRAP (2010) Material bulk densities ROT039 https://www.wrap.ngo/sites/default/files/2021-02/WRAP-bulk-density-summary-report-Jan2010.pdf | technical report, measured | Paper and card in rear-end loaders 431 kg/m³ (375–495, n = 87, CoV 0.07); food 45–711. |
| 47 | Zekkos et al. 2017 (JGGE); Bareither, Benson & Edil 2012 (ASCE); Zhang et al. 2016 | PR (snippets) | MSW compressibility follows log-type stress–strain relations; parameters depend on composition. |
| 48 | HBK, Load application in load cells https://www.hbm.com/tw/3377/load-application-in-load-cells/ | MFR application note | Avoid side loads, bending and torsion; force shunts via stay rods; thermal expansion; pendulum and rocker mounts. |

## 7. Hardware prices (VEN, listed prices unless marked)

See `_research/hardware_prices.md` for every product, part number, price, date and URL. Prices used in `BILL_OF_MATERIALS.md`:

| Item | Listed price | Retailer / URL (from hardware_prices.md) |
|---|---|---|
| ANYLOAD 102ES stainless double-ended shear beam, IP68 | USD 870 (25 klb) | Tacuna Systems |
| Rice Lake RL32018S 10 klb stainless shear beam | USD 440 (search snippet) | Rice Lake (fetch blocked) |
| ANYLOAD 535TS load pin 5 / 10 / 20 t | USD 722 / 868 / 1,194 | Tacuna Systems |
| Micro-Measurements LWK-06-W250B-350 weldable gauge | ≈ USD 292 | DigiKey |
| Gems 3100 0–400 bar | £156 | RS UK |
| Danfoss MBS 3000 060G1109 | £198 ex VAT | RS UK |
| WIKA A-10 400 bar | €264 ex VAT | RS FR |
| Eastron SDM630 Modbus MID V2 | €91 ex VAT | Ropere |
| VEGAPULS C 11 radar | €576 | VEGA shop |
| MaxBotix MB7389 ultrasonic IP67 | €82 ex VAT | distributor |
| Laumas TLE transmitter | ≈ USD 210 | distributor |
| Rice Lake 482 Plus indicator | USD 770–839 | distributors |
| Stainless 4-cell junction box | USD 153–162 | distributors |
| Teltonika RUT956 LTE router | €220 ex VAT | distributor |
| Elkome IP67 tilt sensor | €333 | Elkome |
| WeDi K3 15 t container scale (complete) | €4,800–5,620 ex VAT | 2024 listing |

Unverified: "~€30 400 bar transducer". No public prices: Tamtron, Pfreundt, LCM and Strainsert pins, HBK SLB700A, Finnish installation, verification and type-examination costs (all marked assumptions).
