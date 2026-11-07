# SmartWeight: legal-metrology constraints on weight-based billing (Finland / EU)

Research date: 2026-11-07. Web access worked: WebSearch and WebFetch succeeded. Finlex statute text was downloaded and parsed directly. Some PDFs could not be read: they were encrypted, or the URL redirected or returned 404. Those gaps are marked below.
Evidence types: **LAW** = statute or directive text; **STD** = standard or OIML/WELMEC guide; **REG** = regulator or municipal tariff; **VENDOR** = manufacturer claim; **NEWS** = trade press; **DERIVED** = arithmetic from cited tables (not a source claim).

---

## 1. Summary verdict

- **Weight-based invoicing in Finland is legally controlled metrology, and the parties cannot contract out of it.** The Finnish Measuring Instruments Act (Mittauslaitelaki 707/2011) §2(1)(1) covers any instrument used "in business to determine the price of a product or service or other economic benefit on the basis of measurement results". §3 then *always* covers non-automatic weighing instruments (NAWIs) used to determine mass for trade or for fees, including *hyvitys/korvaus/palkkio* (credits, compensation, remuneration). The only B2B exemption in the Act applies to *consumption metering* (utility-type meters) between medium or larger enterprises. It does not apply to weighing. [LAW]
- **The scale must be class III.** Government Decree 1431/2016 requires an accuracy class III NAWI to determine mass in trade (Act §3(1)). Fees under §3(2) may use class III or IIII. It must be CE + "M" marked after EU conformity assessment (Module B type examination + D or F, or G). It must be verified before first use and re-verified **every 3 years** by a Tukes-approved inspection body (VNa 471/2014). [LAW]
- **A load-cell base or frame built into an Europress compactor or container, read statically, is a NAWI under 2014/31/EU.** Built to class III, it *can* be billing grade. It needs an EU type-examination certificate (or a Module G unit verification), CE+M marking, initial verification, and 3-yearly re-verification. WELMEC 2 already has guidance for vehicle-mounted NAWIs (tilt ≤ manufacturer limit, tilt sensor or switch) and for waste-collection vehicles. [LAW/STD]
- **Class III accuracy is far tighter than a ±2–5% target.** Example: Max 6 000 kg, e = 2 kg. At a 3 000 kg load the MPE is ±2 kg at verification and ±4 kg in service (≈0.07–0.13%). Even a 60 t weighbridge with e = 20 kg gives a worst case of about ±40–80 kg on a 3 000 kg gross-minus-tare net (≈1.3–2.7%). That is inside ±100 kg. [DERIVED from LAW tables]
- **The current Finnish norm is weighing at the receiving waste centre's weighbridge.** For example, the Pirkanmaan Jätehuolto/Tampere 2025 tariff says hooklift containers and compactors are weighed and their treatment fee is weight-based. Rusko/Kiertokaari weighs vehicles on entry and exit scales. The certified ticket from the weighbridge is the de facto billing basis. [REG]
- **Certified on-vehicle options exist, all from vendors.** Tamtron (FI) states its One Power truck on-board scale is "approved for legal for trade" and can be used "as the basis for invoicing". It gives no class or accuracy number. Pfreundt (DE) sells hooklift scales listed as class III/IIII "eichfähig" and conformity-assessed. Bin-lift catchweighers on refuse trucks are MID MI-006 / OIML R51 class Y(a)/Y(b) devices: Botek B6-KV DK cert, Max ≤ 3 500 kg; VWS Enviroweigh, FEL certified to 20 kg. [VENDOR/STD]
- **Uncertified load pins, strain gauges, hydraulic-pressure and fill-level×density estimates are estimate grade.** They can legally be used for internal planning, fill-level and route optimisation, recycling-value forecasts, and plausibility cross-checks of certified tickets. They **cannot** be the measured quantity on which a price, fee, credit or rebate is computed, even if both parties agree. Exception: a contract that prices per emptying or per volume, with no weight-based price, falls outside the Act. Municipal tariffs already do this with standard volume-weights (e.g. 55 kg/m³). [LAW/REG; the interpretation of "agreed estimate" is ours, see Open questions]
- **Cost and time of type examination: no public figure found.** Notified bodies (RISE, NMi, FORCE, Kiwa/Inspecta) quote per project. A Module B certificate is valid for 10 years. A periodic-verification list price of **€89 + VAT** appears on Kiwa Finland's page (applicable instrument size unclear). [REG/VENDOR]

---

## 2. EU NAWI Directive 2014/31/EU

| Claim | Source | Type |
|---|---|---|
| Art. 1(1) applies to all NAWIs. Art. 1(2) lists the regulated uses: (a) determination of mass for commercial transactions; (b) determination of mass for the calculation of a toll, tariff, tax, bonus, penalty, remuneration, indemnity or similar payment; (c) application of laws and expert evidence; (d) medical; (e) pharmacy; (f) price by mass for direct sales to the public/prepackages. Point (g) covers all other uses, which are not subject to the conformity requirements | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014L0031 (accessed 2026-11-07) | LAW |
| Art. 2(2): a NAWI is "a weighing instrument requiring the intervention of an operator during weighing" | same | LAW |
| Art. 13 conformity assessment: Module B (EU-type examination) followed by D (production QA) or F (product verification), or Module G (unit verification). D1/F1 only for instruments without electronics and without springs | same | LAW |
| Art. 16: supplementary metrology marking is a capital "M" plus the last two digits of the year, in a rectangle the same height as the CE mark | same | LAW |
| Annex II: the Module B certificate is valid 10 years | same | LAW |
| Annex I Table 1, class III: 0.1 g ≤ e ≤ 2 g → n = 100–10 000; **e ≥ 5 g → n = 500–10 000**; Min = 20e. Class IIII: e ≥ 5 g, n = 100–1 000, Min = 10e | same | LAW |
| Annex I Table 3 MPE at verification, class III: **±0.5e for 0 ≤ m ≤ 500e; ±1e for 500e < m ≤ 2 000e; ±1.5e for 2 000e < m ≤ 10 000e**. Class IIII: ±0.5e ≤ 50e; ±1e ≤ 200e; ±1.5e ≤ 1 000e. **In service the MPE is twice these values (Annex I §4.2)** | same | LAW |
| Annex I §7.1: class II–IIII instruments that may be used tilted must be sufficiently insensitive to tilt | same | LAW |

**Is a compactor or container weighing system a NAWI?**
- It is a NAWI if the weighing result is taken while the load is at rest and an operator or the system initiates the reading: static weighing of a container on its base frame or load cells, or of a hooklift body after lifting and stopping. WELMEC 2 (2015) §3.1.13 explicitly treats "vehicle mounted non automatic weighing instruments". Type approval requires the manufacturer to define a tilt limit within which the instrument stays inside MPE. Tilt testing goes up to 10%, unless a tilt switch or sensor blanks display, printing and data transmission at a lower tilt. A tilt-compensation sensor counts as an essential part and must undergo temperature, humidity and EMC tests. §3.1.13.2 covers waste collection vehicles, where the eccentric-load test may be done by alternative means (e.g. hanging weights) as decided by the notified body. Source: WELMEC Guide 2 (2015), https://www.laumas.com/pub/norme_direttive/METROLOGIA_LEGALE/NAWI/WELMEC_2.0.pdf (accessed 2026-11-07) [STD]. A newer WELMEC Guide 2 (2023, NAWI/AWI/MDMI) exists at https://www.welmec.org/welmec/documents/guides/2/2023/WELMEC_Guide_2_2023_Guide_for_NAWI_AWI_and_MDMI.pdf. It was not read; check it for updated vehicle text.
- WELMEC 2.4 (load cells) warns that the general acceptance of load-cell test certificates "shall not be applied to weighing instruments built in trucks". Expect more instrument-level testing for vehicle- or container-integrated systems. https://www.welmec.org/welmec/documents/guides/2.4/2-4.pdf (via search snippet, 2026-11-07) [STD]
- If weighing happens automatically during lifting or emptying, without operator intervention or standstill, the instrument is an **automatic** weighing instrument (MID, see §3).

## 3. MID 2014/32/EU Annex VIII (MI-006) and OIML R51 / R76 / R134

| Claim | Source | Type |
|---|---|---|
| MI-006 catchweigher: an AWI that determines the mass of pre-assembled discrete loads or single loads of loose material. Category X covers prepackage checking; **category Y covers all other catchweighers**. Classes Y(I), Y(II), **Y(a), Y(b)** | https://legislation.gov.uk/eudr/2014/32/annex/VIII/data.htm?view=plain (EU text as retained, accessed 2026-11-07) | LAW |
| Y(a): e ≥ 5 g → n 500–10 000. Y(b): e ≥ 5 g → n 100–1 000. Category Y MPE (automatic operation): **±1e (≤500e Y(a) / ≤50e Y(b)); ±1.5e (500–2 000e / 50–200e); ±2e (2 000–10 000e / 200–1 000e)**. Min capacity 20e for Y(a), 10e for Y(b) | same (table partly garbled in the source; values cross-checked against the structure of the category X column) | LAW |
| AWI conformity modules: electronic or software systems use B+D, B+F, G or H1 | same | LAW |
| Chapter I §1.3: for instruments under special mechanical strain, e.g. "instruments incorporated into vehicles", the manufacturer must define the mechanical conditions of use | same | LAW |
| Refuse-vehicle on-board weighing is classed under OIML R51 as category Y catchweighers | IMEKO WC 2000 paper https://www.imeko.info/publications/wc-2000/IMEKO-WC-2000-TC3-P102.pdf (search snippet) | PAPER |
| Danish EC certificate DK0199.408 rev1: Botek **B6-KV**, battery-operated vehicle-mounted automatic catchweigher on a refuse-truck bin lifter (strain-gauge load cells + acceleration/inclination sensor). Basis OIML R51-1:2006, class **Y(a) or Y(b)**, Max 10–3 500 kg. A revision exists as 0200-MID-06144 rev1 | https://sik.dk/sites/default/files/2023-03/midmid_dk0199.408_rev1_2014.pdf ; https://sik.dk/sites/default/files/2023-03/midmid_0200_mid_06144.pdf (PDF encrypted; details from search snippet) | STD (certificate) |
| VWS **Enviroweigh** bin-weighing got EU type approval (Jan 2020) for pay-by-weight. Wheeled bins 0.5% or 1 kg; FEL version "certified to an accuracy of 20 kg", up to 3 500 kg; class Y(b) | https://resourcemedia.eco/article/vws-bin-weighing-system-awarded-eu-approval (accessed 2026-11-07) | NEWS/VENDOR |
| OIML R134 covers automatic instruments for weighing **road vehicles in motion** and measuring axle loads (weigh-in-motion). It does not apply to static container net weighing | https://www.oiml.org/en/files/pdf_r/r134-1-e06.pdf (title/annex via search) | STD |
| OIML R76 is the international counterpart of the NAWI essential requirements (EN 45501 is the harmonised standard). Its class III table is the same as the Directive table above | EN 45501 cited in FINAS scope https://www.finas.fi/Scopes/I001_Liite_1_29_M45_2025.pdf (search snippet) | STD |
| EN 15430-1 (on-board weighing for refuse collection vehicles) | **Not found.** No text or summary was retrievable. The related standard **EN 14803** (identification and/or determination of quantity of waste) covers weighing systems (AWI and NAWI), on-board computers and data transfer: https://standards.iteh.ai/catalog/standards/cen/be813ea3-0ab7-4ca7-8113-eee85f2dcb98/en-14803-2020a1-2024 | STD |

### Worked numbers [DERIVED from the 2014/31/EU Annex I tables]

**A. Class III, Max 6 000 kg, e = 2 kg (n = 3 000)**

| Load band | MPE at verification | MPE in service |
|---|---|---|
| 0–1 000 kg (≤500e) | ±0.5e = ±1 kg | ±1e = ±2 kg |
| 1 000–4 000 kg (≤2 000e) | ±1e = ±2 kg | ±2e = ±4 kg |
| 4 000–6 000 kg (≤3 000e) | ±1.5e = ±3 kg | ±3e = ±6 kg |

At 3 000 kg the MPE is ±2 kg / ±4 kg, i.e. **0.07% / 0.13%**. This is about 25–50 times tighter than ±100 kg and far inside ±2–5%. Min = 20e = 40 kg.

**B. Class III, Max 10 000 kg, e = 5 kg (n = 2 000)**: 0–2 500 kg ±2.5 kg; 2 500–10 000 kg ±5 kg at verification, doubled in service. At 3 000 kg: ±5 / ±10 kg (0.17% / 0.33%). With e = 10 kg (n = 1 000): ±5 kg up to 5 t, ±10 kg up to 10 t (in service ±10 / ±20 kg).

**C. Typical weighbridge, class III, Max 60 t, e = 20 kg (n = 3 000)**: 0–10 t ±10 kg; 10–40 t ±20 kg; 40–60 t ±30 kg at verification, doubled in service. A hooklift truck with a container (gross ~15–30 t) falls in the 10–40 t band. **Net = gross − tare (two weighings)**, worst case is the sum of the two MPEs: **±40 kg at verification / ±80 kg in service on a 3 000 kg net (1.3% / 2.7%)**. The root-sum-square would be ~±28 / ±57 kg. Rounding to e = 20 kg adds up to ±10 kg per reading (already inside MPE). The result is still within ±100 kg but takes much of a ±2% budget. Note: a 3 000 kg net is only 150e on a 20 kg-e bridge. The Directive does not forbid this. Some regulators impose a minimum net (e.g. Wisconsin: divisions > 2 kg shall not weigh net loads < 500 d: https://datcp.wi.gov:443/Documents/OnBoardWeighingSystems.pdf, US example only). The Finnish rule is not found.

## 4. Finland: national rules

| Claim | Source | Type |
|---|---|---|
| **Mittauslaitelaki 707/2011 §2(1)**: the Act applies when an instrument is used (1) *elinkeinotoiminnassa tuotteen tai palvelun hinnan taikka muun taloudellisen edun määrittämiseen mittaustulosten perusteella* (in business, to determine price or other economic benefit from measurement results); (2) in consumption metering, **excluding cases where both parties are medium-sized or larger enterprises (2003/361/EC)**; (3) authority decision-making; (4) public interest, health, safety, order or environmental protection | Finlex, consolidated version 2025-06-27 https://www.finlex.fi/fi/lainsaadanto/2011/707 (accessed 2026-11-07) | LAW |
| **§3**: the Act applies to NAWIs used for (1) mass for trade; (2) mass for customs, *kuljetusmaksu* (transport fee), tax, ***hyvitys*** (credit/rebate), fine, ***palkkio***, ***korvaus*** or similar payment; (3) laws and expert evidence; (4) medical; (5) pharmacy; (6) price by mass in direct sales and prepackaging. "The Act always applies to NAWIs referred to in §3" | same | LAW |
| The instrument must not be put into use before conformity has been shown and reliability verified. For §2(1)(1)–(2) and §3 instruments, initial verification is done by a notified body or inspection body (or by the manufacturer under a notified-body-approved procedure) | same | LAW |
| The operator (*toiminnanharjoittaja*) is responsible for suitability, continued reliability and verification at the prescribed intervals. **In-service verification must use an inspection body (*tarkastuslaitos*)**. When price is determined, the instrument must be placed so the weighing and the display are observable by the parties. Tare must be used for bulk goods | same | LAW |
| **VNa 1431/2016 (NAWI decree)**: trade (§3(1)) and direct sales (§3(6)) **must use class III**. Fees under §3(2) and soil/aggregate trade use class III or IIII. Precious metals use class I/II. Ancillary devices not conformity-assessed must bear the restricted-use mark | https://www.finlex.fi/fi/lainsaadanto/2016/1431 (accessed 2026-11-07) | LAW |
| **VNa 471/2014 (measuring instruments decree)**: applies to §2(1)(1) instruments and §3(1),(2),(6) NAWIs. **"Mittauslaite on varmennettava kolmen vuoden välein käyttöönoton jälkeen"** (verify every 3 years after commissioning). Fuel/gas dispensers and automatic checkweighers are on a shorter interval (text truncated; Kiwa says 2 years). The inspection body may move the date ±4 months. Verification is marked by a crown mark + date + body ID. The operator must supervise use and keep a log. Inspection bodies are approved by Tukes | https://www.finlex.fi/fi/lainsaadanto/2014/471 (accessed 2026-11-07) | LAW |
| Kiwa Finland: periodic verification of scales every 3 years, line scales every 2 years. Initial verification (ensivarmennus) offered. Online list price **€89 + 25.5% VAT** (final price depends on site; instrument size unclear) | https://www.kiwa.com/fi/fi/palvelutyyppi/kalibrointi-ja-varmennus/mittauslaitteiden-varmennus/ (accessed 2026-11-07) | VENDOR |
| Tukes is the market-surveillance authority for NAWI and MID instruments and supervises legal metrology. In-service surveillance is run with the regional authorities. Class III is the general minimum, IIII is allowed for tolls and freight | WELMEC country info Finland https://welmec.org/legal-metrology-information/country-information/country/finland and PDF https://www.welmec.org/welmec/documents/Country_Information/Finland.pdf (PDF not text-extractable; points via search snippet) | REG |
| Finnish NAWI notified body: Inspecta Tarkastus Oy (now Kiwa), **NB 0424** (a Module D certificate seen, expired 2025-11-29). Check current scope in NANDO | Search snippet referring to https://lahtiprecision.fi-p.seravo.com/wp-content/uploads/2023/06/Ensivarmennusoikeus-NAWI-EN-2023.pdf | VENDOR (certificate) |
| VTT MIKES (national metrology institute): role in waste weighing **not found**. It maintains national standards and traceability; it does not verify trade scales | no source retrieved | — |
| **Jätelaki 646/2011 §78**: the municipality must charge a waste fee that covers the cost of the waste management it organises. The tariff structure is set locally | e.g. Järvenpää tariff via search (https://jarvenpaa.cloudnc.fi/…) | LAW (via municipal doc) |
| **Pirkanmaan Jätehuolto / Tampere waste tariff 1.1.2025**: "*Vaihtolavasäiliöt punnitaan ja niiden käsittelymaksu määräytyy painoperusteisesti*" and "*Vaihtolavasäiliön, vaihtolavan ja puristinten käsittelymaksut määräytyvät painoperusteisesti*". Mixed-waste treatment fee 125 €/t (VAT 0). For unweighed containers it uses a standard volume-weight of **55 kg per container-m³** for mixed waste. Weight-based loads must be pre-notified in MaterialPort | https://tampere.fi/sites/default/files/2024-12/Jatetaksa-1.1.2025-alkaen.pdf (accessed 2026-11-07; text extracted from PDF streams) | REG |

## 5. Onboard weighing products (refuse, hooklift, skip)

| Vendor / product | Certification claim | Accuracy claim | Source | Type |
|---|---|---|---|---|
| **Tamtron (FI) One Power Truck On-board Scale**: trucks, trailers, translifters; waste & recycling | "approved for legal for trade". Weighing data "can be used as the basis for invoicing". No class, certificate number or standard stated | none stated | https://tamtron.com/en/product/one-power-truck-on-board-scale (accessed 2026-11-07) | VENDOR |
| Tamtron truck scales (weighbridges) | "EU type-approved", OIML class III (search snippet) | — | https://tamtrongroup.com/en/product/tamtron-truck-scale | VENDOR |
| Tamtron One Timber Crane Scale | EU MID type approval (Sept 2025) | 1–2% of total load (distributor) | https://tamtrongroup.com/en/mfn_news/tamtron-one-timber-crane-scale-approved-for-legal-trade/ ; https://forestmachinemagazine.com/tamtron-one-timber-crane-scale-receives-eu-type-approval/ | VENDOR/NEWS |
| Tamtron Scalift 200 forklift | MID automatic weighing type approved | ±0.1% of Max | https://tamtrongroup.com/wp-content/uploads/2025/04/DN15688_4-EN_Brochure-Scalift-Forklift-Scale_250404.pdf (snippet) | VENDOR |
| Tamtron hooklift-specific scale | **Not found** | — | — | — |
| **Pfreundt (DE) hook-lift scale (WK60 electronics)**: weighs after hydraulic lifting of the container | Portfolio lists hooklift scales as class **III + IIII, "eichfähig"**. WK60 "durch PFREUNDT konformitätsbewertet" for trade. An OIML certificate exists for WK60 as an "automatic catchweigher integrated into a hydraulic system of front-end loaders and other vehicles" | No MPE stated publicly | https://pfreundt.de/en/products/hook-lift-scale ; https://www.pfreundt.de/fileadmin/images/broschueren/PFREUNDT-Produktportfolio_2024_01.pdf (snippets, accessed 2026-11-07) | VENDOR |
| **RDS / Welvaarts calibrated body weighing (compactor trucks)**: superstructure weighed before and after each pickup → net per customer | "legal-for-trade total weighing system" | none stated | https://rds.eu/en/product/calibrated-body-weighing-system (accessed 2026-11-07) | VENDOR |
| Botek B6-KV bin-lifter | EC/MID cert, OIML R51 Y(a)/Y(b) | class-based, Max ≤ 3 500 kg | DK0199.408 (above) | certificate |
| VWS Enviroweigh | EU type approval, Y(b) | FEL: 20 kg; bins 0.5% / 1 kg | above | NEWS |
| Rice Lake TradeRoute HL (N. America) | NTEP + Measurement Canada | — | https://www.ricelake.com/products/traderoute-hl-series/ | VENDOR (non-EU) |
| Vishay/BLH Nobel, Loadmaster, Haenni/Intercomp hooklift approvals | **Not found** | — | — | — |
| Historic UK: Red Forge on-board system, "Class 3", within 2.5 kg up to 10 t on slopes up to 5% | — | — | https://archive.commercialmotor.com/article/13th-december-2001/15/weighing-up-waste-invoices (2001) | NEWS |

Ireland's regulator states that bin-weighing systems on refuse trucks are under legal metrological control when used for trade: https://www.oireachtas.ie/en/debates/question/2016-07-12/803/ (snippet) [REG, IE].

## 6. Billing practice in Finland and the Nordics

- In Finland the waste centre's weighbridge is the billing point for containers and compactors. Pirkanmaa: containers and compactors are weighed, and the treatment fee is weight-based. Kiertokaari/Rusko: "The charge is determined according to the weight of your load"; vehicles cross entry and exit scales, with mid-weighings for mixed loads. https://kiertokaari.fi/rusko-waste-management-centre-service-instructions/ (accessed 2026-11-07) [REG]
- The hauler's *transport/emptying* fee is generally per emptying or per container size, not per kg (Tampere/Vestia tariffs) [REG]. So a customer invoice typically = per-lift transport fee + €/t treatment fee × weighbridge net weight.
- Weighbridge class: Finnish law requires class III for trade. The typical e of 20 kg for 60 t is an industry convention, not found in a Finnish source; see the worked numbers in §3C. Exact tare practice for hooklift container net weighing (stored tare vs. exit weighing) is **not found** in the Finnish sources.
- Nordic (SE/NO/DK) practice: **not researched in depth / not found**.

## 7. Can non-certified "indicative" weights be used?

Legal basis: Act 707/2011 §2(1)(1) and §3 (above). Our interpretation:

| Use | Allowed with uncertified weight? | Reasoning |
|---|---|---|
| (a) Recycling-value *estimates* (forecast, dashboard, "your bale is worth ~€X") | **Yes, if purely informative.** **No** if a credit or rebate (*hyvitys*) or purchase price is actually computed from it | §3(2) names *hyvitys* and *korvaus* explicitly; §2(1)(1) covers "other economic benefit" |
| (b) Internal planning, fill-level, pickup scheduling, overload warning | **Yes** | Not price determination; outside §2/§3 (2014/31 Art 1(2)(g) "other uses") |
| (c) Cross-checking certified tickets, anomaly/fraud detection | **Yes** | The invoice remains based on the certified ticket. An uncertified weight may trigger a dispute, but it is not the billing basis |
| (d) Contract where both parties agree to bill on an estimated weight | **Not permitted for weight-based pricing.** The Act has no consent exemption for weighing; the only B2B exemption is for consumption metering between medium+ enterprises (§2(1)(2)). Permitted alternative: price per emptying or per volume/fill level (not a mass measurement) | LAW + interpretation. Confirm with Tukes (see Open questions) |

## 8. Cost and time of certification

- EU type examination (Module B), NAWI or MID: **no public price or duration found**. Notified bodies quote per project (RISE Sweden; NMi NL flyers https://nmi.nl/wp-content/uploads/2019/07/Flyer-NAWI-2019.pdf; FORCE DK; Kiwa/Inspecta FI). A WELMEC/OIML training slide notes that time to market is "relatively long". https://report.nat.gov.tw/ReportFront/PageSystem/reportFileDownload/C10502217/003 (snippet) [STD]
- Certificate validity: 10 years (Directive Annex II) [LAW]. A Module D QA system or Module F per-unit verification is needed for production on top of Module B. Alternative for a few one-off units: **Module G** (unit verification by the notified body, no type certificate).
- **Cheaper route (inference):** integrate an already type-approved indicator and OIML R60 load cells via the WELMEC modular approach (WELMEC 2.10, https://welmec-upgrade.bs.ptb.de/welmec/documents/guides/2.10/2021/WELMEC_Guide_2.10_issue_1_v2021.pdf), or partner with a vendor holding an approval (Tamtron, Pfreundt). Caveat: WELMEC 2.4 excludes truck-built instruments from general load-cell acceptance.
- Periodic verification: every 3 years. Kiwa list price €89 + VAT (scope unclear). Weighbridge verification price **not found**. UK local-authority 2018/19 example: £85.56/h, NAWI ≤ 1 t £112.56 (https://caerffili.gov.uk/CaerphillyDocs/Trading-Standards/Metrology_Fees-(1).aspx; UK, dated, indicative only).
- Order-of-magnitude for Module B cost: **not found; any figure would be a guess.** Get quotes.

---

## 9. Approach classification

| Candidate approach | Billing grade possible? | What is required | Typical certified accuracy |
|---|---|---|---|
| **Certified platform / load cells in compactor or container base** (static, NAWI) | **Yes** | Class III NAWI: EU type exam (B) + D/F, or G per unit. CE+M. Tilt limit/sensor per WELMEC 2. Initial verification. Re-verify every 3 years (Tukes-approved inspection body). Display observable by parties. Tare handling. Sealed data path to the invoice | Class III. E.g. e = 5 kg, Max 10 t: ±5 kg verification / ±10 kg in service at 3 t (≤0.33%) [DERIVED] |
| **Onboard hooklift/skip truck scale** (static after lift → NAWI; during lift → MID MI-006 catchweigher) | **Yes, if type-approved** (Pfreundt claims class III/IIII; Tamtron claims legal-for-trade; class not published) | Vendor's EU type certificate + verification of each truck installation + 3-yearly re-verification. The hauler is the operator, so Europress depends on the hauler | Class III/IIII (Pfreundt, no MPE published). Catchweighers Y(a)/Y(b), e.g. 20 kg FEL (Enviroweigh) |
| **Hauler / waste-centre weighbridge net ticket** (gross − tare) | **Yes, current norm** | Class III weighbridge, verified every 3 years; stored or measured tare | e = 20 kg @ 60 t: ±40 kg (verification) to ±80 kg (in service) worst case on a 3 t net (1.3–2.7%) [DERIVED] |
| **Uncertified load pins / strain gauges** in compactor or container | **No (estimate grade)**, unless later type-approved as above | — | Not certified. Vendor-dependent, not found |
| **Hydraulic-pressure estimate** (lift cylinder / compactor ram pressure) | **No (estimate grade)**. Pfreundt's hydraulic system shows pressure-based weighing *can* be type-approved, but only as a specific certified instrument | Would need full type approval incl. temperature/friction compensation | Not certified as generic. Tamtron hydraulic crane/loader scales claim 1–2% |
| **Fill-level × density estimate** | **No** for mass-based pricing. **Yes** as a volume-based tariff (no mass claimed), as municipalities do with 55 kg/m³ | Contract priced per volume or emptying, not per kg | n/a. Density variance dominates |

## 10. Open questions and uncertainties

1. **Tukes interpretation** of a contract price per kg based on an agreed estimate, or "indicative weight" invoices with certified-ticket true-up. Our reading is that it is not allowed, but no Tukes guidance text was found. Ask Tukes (mittauslaitteet) directly.
2. Whether automatic in-cycle weighing in an Europress compactor (no operator intervention) would be MID MI-006 Y(a)/Y(b) instead of NAWI. This depends on the operating mode and the notified body's view.
3. **EN 15430-1** content and status: not found.
4. Tamtron: no hooklift-specific product, certificate number, class or MPE found. The brochure PDF returned 404 on redirect.
5. Pfreundt hook-lift: no published MPE or e. The certificate numbers were not retrieved.
6. Current Finnish NAWI notified bodies and scopes in NANDO: not verified (Inspecta/Kiwa NB 0424 likely).
7. Certification cost and time: not found. Weighbridge periodic verification price in Finland: not found.
8. Whether Finnish waste centres use stored tare for hooklift containers, and whether a minimum net load rule applies: not found.
9. MI-006 MPE table on legislation.gov.uk was partly garbled. The values should be checked against the official EUR-Lex 2014/32/EU Annex VIII.
10. The WELMEC 2 guide read was the 2015 edition (Directive 2009/23/EC). The 2023 edition was not read.
