# SmartWeight – hardware specs & price evidence (retrofit weighing on compactors / hooklift containers)

Compiled 2026-11-07 using WebSearch and WebFetch. Web access worked, with some gaps:
- Some retailer pages blocked WebFetch (HTTP 403/429: ricelake.com, weightechusa.com, measurementshop.co.uk).
- PDF datasheets could not be parsed because no PDF tooling was available.
- For those, the figures come from search-result snippets of the retailer page. They are marked "snippet".

**How to read the tables**
- **Date** = the date the price was retrieved (2026-11-07). Listing dates are mostly not shown on the pages. A few listings show their own date, noted as e.g. "listing upd. 2024-06".
- **Price status**
  - `confirmed (listed price)`: a public web-shop or list price was seen on the page or in its indexed snippet.
  - `estimate (quote-only / derived)`: the price is not published, or was derived from a related model.
- **VAT**: "ex VAT" / "inc VAT" is stated where the source showed it.
- **Specs**: specs not re-verified in this session are tagged **[verify]**.
- **Accuracy class**: OIML R60 C3 means accuracy class C with 3000 verification intervals (nmax = 3000). It is the usual minimum for legal-for-trade (R76 class III) multi-cell scales.

---

## 1. Load cells (shear beam / double-ended shear beam / compression), 2–10 t, plus weigh modules

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| Zemic H8C single-ended shear beam (alloy, Ni-plated) | H8C-C3-5.0t-4B | 5 t, OIML R60 C3 approved, IP67/IP68 depending on seller (listings disagree), alloy steel not stainless | 220 (Brecknell list) / 175–550 GBP range at Measurement Shop | USD / GBP | 2026-11-07 (price list undated) | https://www.centralcarolinascale.com/PDF/BRECKNELL/Brecknell-Shear-Beam-Load-Cells.pdf ; https://www.measurementshop.co.uk/products/h8c-zemic-shear-beam-load-cells | confirmed (listed price), snippet |
| Zemic HM8 stainless shear beam | HM8-C3-5.0t | 5 t, stainless, C3 | 360 | USD | 2026-11-07 (list undated) | https://www.centralcarolinascale.com/PDF/BRECKNELL/Brecknell-Shear-Beam-Load-Cells.pdf | confirmed (listed price), snippet |
| Zemic Europe BM8H stainless SB, IP68 | BM8H-C3-5t-6B-A1 | 5 t, stainless, IP68, C3 | n/a | – | 2026-11-07 | https://www.electronicsdatasheets.com/manufacturers/zemic-europe/parts/bm8hc35t6ba1 | estimate (quote-only) |
| Rice Lake RL32018S stainless single-ended beam | RL32018S 10,000 lb (≈4.5 t) | stainless, hermetic, NTEP / OIML C3 [verify] | 440 (list, 20 ft cable); alloy RL32018: 398 | USD | 2026-11-07 | https://ricelake.com/products/rice-lake-rl32018s-stainless-steel-single-ended-beam-load-cell | confirmed (listed price), snippet |
| Flintec SB14 stainless single-ended beam | 41170 (5,000 lb CU) | 227–4,536 kg range (no 5 t), stainless, IP68 hermetic, OIML approved | 493 (Rice Lake list) | USD | 2026-11-07 | https://ricelake.com/products/flintec-sb14-stainless-steel-single-ended-beam-load-cell | confirmed (listed price) |
| ANYLOAD 102ES stainless double-ended shear beam | 102ES-25klb (smallest ≥10 t) | 17-4PH stainless, IP68, 3 mV/V, creep <±0.030 %/30 min, TC zero <±0.0040 % Cn/K, TC span <±0.0012 % Cn/K, compensated −10…+50 °C, service −30…+70 °C | 870 (1–9 pcs); 730 for ≤5 klb; −15 % at 100+ | USD | 2026-11-07 | https://tacunasystems.com/products/load-cells/double-ended-shear-beam/anyload-102es-stainless-steel-double-ended-beam-load-cell/ | confirmed (listed price) |
| ANYLOAD 102BS stainless DESB (truck-scale class) | 102BS-25klb…75klb | 2Cr13 stainless, IP68 welded, OIML C5 (11–55 t) / NTEP IIIL 10000d, creep <±0.023 %, same TCs as above | 846 (25 klb); 1,250 (40–75 klb) | USD | 2026-11-07 | https://tacunasystems.com/products/load-cells/double-ended-shear-beam/anyload-102bs-stainless-steel-double-ended-beam-load-cell/ | confirmed (listed price) |
| Chinese DESB "10t/20t" (Made-in-China) | n/a | DESB, claims Zemic/MT compatibility; spec and OIML certificate unverified | 75.50 (MOQ 10) | USD | 2026-11-07 | https://www.madeinchina.com/mall/show-10t-20t-Double-Ended-Shear-Beam-Mettler-Toledo-Zemic-Digital-Load-Cell_1343059.html | confirmed (listed price), low credibility |
| Mettler Toledo SWB805 MultiMount weigh module | e.g. 30131952 (2.2 t SS C3) | 110 kg–4.4 t, stainless, C3 (no 5 t in range) | not published ("Get your quote") | – | 2026-11-07 | https://www.mt.com/au/en/home/products/Industrial_Weighing_Solutions/load-cell-and-weigh-module/compression-wmlc/weigh-module-swb805-ss-2-2t-5k-c3-30131952.html | estimate (quote-only) |
| Rice Lake RL1800 weigh module hardware (mount only, no cell) | RL1800 SS 10,000 lb LE | stainless mount | 695 (mount only); complete 5,000 lb SS kit (cells + J-box + cable) 4,650 | USD | 2026-11-07 | https://www.ricelake.com/products/rl1800-series-with-mlc-coated-load-cell-weigh-module-kit?print=true | confirmed (listed price), snippet |

**Notes on industrial suitability**
- **Cell choice for a hooklift subframe or container support.** Use a stainless (17-4PH or 2Cr13) welded/hermetic **IP68** double-ended shear beam or single-ended shear beam.
- **Avoid potted or glued IP67 alloy cells.** Washdown and road salt corrode Ni-plated alloy cells. Freeze–thaw also attacks glued or potted seals.
- **Low temperature (Finland, down to −30 °C).** Most datasheets give a *compensated* range of −10…+50 °C and a *service* range of −30…+70 °C, so at −30 °C the TC errors apply. Example: ANYLOAD TC zero 0.004 % of Cn per K. Over ΔT = 40 K that is about 0.16 % of capacity zero shift. This is why auto-zero or tare per lift cycle is needed.
- **Realistic street price per cell:**
  - Branded stainless C3 cell, 5–10 t: **≈ USD 400–900**.
  - Alloy C3 cell: ≈ USD 200–400.
  - Chinese no-name: < USD 100. The C3 claim is unverified, and these cells need an OIML R60 certificate (look up the number on oiml.org) before use in any trade application.
- **Mounting.** Mounting hardware (rocker/self-aligning weigh modules, anti-lift-off) often costs as much as the cell. Rice Lake's mount alone is USD 695.
- **Budget for 4 cells.** A 4-cell set of branded stainless cells with mounts plausibly costs **€3–6 k** in hardware. This is an estimate derived from the table.

---

## 2. Load pins (instrumented clevis pins), 5–20 t

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| ANYLOAD 535TS stainless load pin | 535TS-5t / -10t / -20t | 2Cr13 stainless, IP67, 1 mV/V ±10 %, non-lin <±0.5 %, hysteresis <±0.5 %, creep <±0.2 %/30 min, TC zero & span <±0.02 % Cn/K, compensated −10…+50 °C | 5 t: 722; 10 t: 868; 20 t: 1,194 | USD | 2026-11-07 | https://tacunasystems.com/products/load-cells/load-pin/anyload-535ts-stainless-steel-load-pin/ | confirmed (listed price) |
| ANYLOAD 535TS (other retailer) | 535TS-10t-YZ | 10 t, IP67, 10 m cable, 150 % safe overload | 1,194 | USD | 2026-11-07 | https://www.scalesplus.com/anyload-535ts-10t-yz-load-pin | confirmed (listed price) |
| Sensy 5000/5300 load pin | 5300 20T-30T SL | 20 t (set for 30 t), 4–20 mA (16 mA span) amplified, IP65, stainless; IP67/68 options in series | 1,318.20 | USD | 2026-11-07 | https://www.telematic.com/Product/wxeqK/5000-Custom-Load-Pin | confirmed (listed price) |
| Strainsert clevis load pin (CPA/CBA) | CPA/CBA series | 1,500–800,000 lb, custom-made; capacity not stated for the listed price | 299.99–599.99 (reseller, capacity unspecified, implausibly low for custom pins) | USD | 2026-11-07 | https://maden.co/products/precision-load-pins-cpa-cba-series-1 | estimate (unreliable listing; treat as quote-only) |
| LCM Systems LMP / LPC stainless load pins | LMP, LPC | from 0.5 t (LMP) / 1–1500 t (LPC), stainless, IP67, custom geometry | not published | – | 2026-11-07 | https://scigate.com.sg/images/stories/scigate/products/lcm/LMP%20Stainless%20Steel%20Load%20Measuring%20Pin.pdf | estimate (quote-only) |

**Notes on industrial suitability**
- **Fit.** A load pin replaces an existing pivot or clevis pin, for example the hooklift tipping pivot or the compactor container hook. That makes it the least invasive retrofit for mechanical integration.
- **Custom geometry.** Real pivots are almost always custom diameters and lengths, so expect custom pins at roughly **€1.5–4 k each**. This is an estimate: the catalogue pins above cost USD 0.7–1.3 k but rarely fit existing pivots.
- **Accuracy.** Pin accuracy is only ~0.5–1 % FS, with sensitivity to load direction and friction. That is enough for fill-level and overload checks, but not for OIML trade.
- **Mounting.** Anti-rotation keeper plates are mandatory. Prefer amplified 4–20 mA versions for long cable runs on vehicles.

---

## 3. Weldable / bolt-on strain sensors, foil gauges, kits

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| HBK SLB700A strain transducer (bolt-on) | 1-SLB700A/06-1 (passive); 1-SLB700A/06VA2-1 (4–20 mA) | bolt-on with 4 screws, ±500 µm/m, IP67 [verify], meant for structures and presses | not published ("Estimate required") | – | 2026-11-07 | https://www.hbkworld.com/en/products/transducers/strain/strain-sensors/slb700a | estimate (quote-only) |
| Micro-Measurements LWK weldable gauge | LWK-06-W250B-350 | weldable (spot-weld shim), 350 Ω, steel-matched (06) | 291.88 (1 pc); 259.32 @25; EU sites ≈ €250–272 | USD / EUR | 2026-11-07 | https://www.digikey.co.uk/en/products/detail/micro-measurements-division-of-vishay-precision-group/LWK-06-W250B-350/10412806 | confirmed (listed price) |
| Micro-Measurements CEA weldable-type foil gauge | CEA-06-UW250A-350 | foil gauge for spot-weld / bond, 350 Ω | 54.55 | USD | 2026-11-07 | https://abra-electronics.com/sensors/sensors-flex-force-en/cea-06-uw250a-350-linear-weldable-strain-gauge-5-0-230-5-84mm-0-169-4-30mm.html | confirmed (listed price) |
| Encardio EDS-20V-AW arc-weldable vibrating-wire gauge | EDS-20V-AW | arc-weldable, VW (needs VW reader) | 75.00 (sold out) | USD | 2026-11-07 | https://shop.encardio.com/products/eds-20v-aw | confirmed (listed price) |
| Chinese 2-hole bolt-on strain sensor | PPM-YB-3000 | bolt-on, full bridge; spec unverified | 150 (EXW) | USD | 2026-11-07 | https://m.madeinchina.com/mall/show-Manufacturer-2-Hole-Bolt-On-Strain-Gauge-Pressure-Sensor-Weight-Sensor-Strain-Gauge_108272.html | confirmed (listed price), low credibility |
| Omega SGD-…-LY41 foil gauges (LY41-type), pack of 10 | SGD-2/350-LY41 | linear foil, 350 Ω, steel TC | 133.45 / 10 pcs | USD | 2026-11-07 | https://rspsupply.com/p-778618-omega-sgd-2350-ly41-strain-gages-pack-of-10.aspx | confirmed (listed price), snippet |
| Phase IV weld-on wireless strain sensor (system) | – | full-bridge weld-on sensor + wireless node | 799 | USD | 2026-11-07 | https://www.phaseivengr.com/product/sensors/strain-gauge/wireless-torsional-strain-sensor-dual-half-bridge/ | confirmed (listed price) |
| Datum Electronics 2-/3-hole bolt-on strain sensors | – | bolt-on, industrial | not published | – | 2026-11-07 | https://www.directindustry.com/prod/datum-electronics/product-181580-1845224.html | estimate (quote-only) |

**Notes on industrial suitability**
- **What these sensors measure.** Structural strain sensors on the hooklift arm or subframe measure *strain*, not weight. The relationship to payload depends on load position, hook geometry, temperature gradients and bolt slip.
- **Calibration and accuracy.** Each truck or body needs in-situ calibration with known loads. Expect **1–3 % FS** after temperature compensation; zero drift from sun-heated steel is the main issue.
- **Installation cost.** Bare foil gauges are cheap (USD 5–30 each). Field installation (surface prep, bonding, protection coating such as M-Coat/AK22, cable strain relief) is the real cost, and outdoor bonded gauges need extensive sealing to survive Finnish winters.
- **Preferred options.** Weldable or bolt-on sealed transducers (HBK SLB700A, Datum) are preferable to bare gauges for a repeatable product.
- **SLB700A budget.** Budget **€500–1,000 each**. This is an estimate: quote-only, and no public price was found.

---

## 4. Hydraulic pressure transducers (0–250/400 bar)

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| WIKA A-10 | 12719341 (0–400 bar, G1/4, 4–20 mA) | non-linearity 0.5 % (per listing), IP65 (IP67 option) [verify], −30…+80 °C [verify] | 301.51 ex VAT | USD | 2026-11-07 | https://tameson.com/products/12719341-0-to-400bar-wika-pressure-transducer-g1-4inch-0p5-4-20-ma | confirmed (listed price) |
| WIKA A-10 (RS France) | RS 221-8287 / 12726673 | 0–400 bar, 4–20 mA, gauge | 263.77 ex VAT (316.52 inc) | EUR | 2026-11-07 | https://fr.rs-online.com/web/p/capteurs-de-pression/2218287 | confirmed (listed price), snippet |
| Danfoss MBS 3000 | 060G1109 (0–400 bar) | 4–20 mA, 10–30 V, G1/4, compact industrial; accuracy ≤±0.5 % FS typ, −40…+85 °C [verify] | 197.76 ex VAT | GBP | 2026-11-07 | https://www.mandmcontrols.com/060g1109 | confirmed (listed price) |
| Gems 3100 | 3100B0400S05G000 / 3100S0400S01B000 | 0–400 bar, current or analogue output, stainless, ±0.25 % FS [verify] | 155.92 / 176.35 | GBP | 2026-11-07 | https://uk.rs-online.com/web/p/pressure-sensors/0314200 | confirmed (listed price; RS "indicative") |
| RS PRO 400 bar sensor | RS 175-4989 | 100/400 bar, 0.5–4.5 V or 4–20 mA option | 166.98 ex VAT | GBP | 2026-11-07 | https://uk.rs-online.com/web/p/products/1754989 | confirmed (listed price), snippet |
| Telemecanique XMLP 6000 psi (≈414 bar) | XMLP6K0PD730 | 316L, 0–10 V, 24 VDC | 139.59 | USD | 2026-11-07 | https://www.zoro.com/telemecanique-sensors-pressure-transmitter-6-000-psi-xmlp6k0pd730/i/G0200499/ | confirmed (listed price) |
| Autonics TPS30 40 MPa | TPS30-G… | 400 bar, 1/4 NPT, 4–20 mA | 193 | USD | 2026-11-07 | https://www.tequipment.net/Autonics/TPS30-G5CAN4-00/Pressure-Transducers/Transmitters/ | confirmed (listed price), snippet |
| Generic Chinese stainless G1/4 0.5–4.5 V transducer | n/a | 5 V ratiometric, ranges listed up to 1000 psi (≈69 bar) on the retailer seen; 400 bar versions exist on AliExpress but were **not found/priced in this session** | 36.95–47.95 (+12.99 ship) for ≤1000 psi | USD | 2026-11-07 | https://www.fruugo.us/pressure-transducer-g14-sensor-5v-input-05-45v-output-0-5v-for-liquid-and-gas-applications/p-359517174 | confirmed (listed price) for low ranges; **400 bar ~€30 = estimate (not verified)** |

**Notes on industrial suitability**
- **Cheapest workable approach.** Hydraulic pressure is the cheapest proxy for weight on a hooklift or tipper: payload ≈ (p·A·lever-arm geometry) at a defined arm position.
- **Error sources.** Cylinder friction, seal hysteresis, dynamic pressure peaks and arm angle typically limit accuracy to **±2–5 % of payload**. That is enough for fill and overload checks, not for billing.
- **Measurement protocol.** Measure at a fixed angle, during slow steady lifts, with an inclinometer and temperature input.
- **Branded transducers.** Units at €150–300 have an industrial EMC rating and IP65–IP67 (DIN or M12 connector). Use a connector with an IP67 cable socket or an over-moulded cable for washdown.
- **Cheap 0.5–4.5 V OEM units.** They have no EMC or overpressure documentation, the 5 V ratiometric signal is noise-prone on a 24 V vehicle harness, and pressure-spike survivability is typically 2× FS, unrated against hydraulic surges.
- **Recommendation.** Use them for prototypes only, or select an automotive-grade OEM such as Sensata, Danfoss MBS 1250, or WIKA MH-4 (quote-only).

---

## 5. Linear position / draw-wire sensors

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| TE/Celesco SP2 string pot | SP2-50 | 50 in (1.27 m), 10 kΩ potentiometer, compact, IP50-ish [verify] | 354.56 (Richardson) / 331.88 (Future) / £522.37 (RS UK) | USD / GBP | 2026-11-07 | https://shop.richardsonrfpd.com/Products/Product/SP2-50 | confirmed (listed price) |
| Micro-Epsilon wireSENSOR WDS-1500-P60 (used/resale) | WDS-1500-P60-CR-A | 1.5 m, industrial, SSI encoder (P+F AVM10) | 523.26 | EUR | 2026-11-07 | https://www.sparepartsnow.de/produkte/micro-epsilon-micro-epsilon-wds-1500-p60-cr-a-c47vfy | confirmed (listed price), resale |
| ASM posiwire WS10 (Ex version) | WS10-1250 EX | 1.25 m, Ex-proof variant | 2,825 | NZD | 2026-11-07 | https://www.u-buy.co.nz/product/MP3JUL2LC-asm-wire-pull-displacement-sensor-ws10-1250-wire-pull-ex | confirmed (listed price), not representative of the standard WS10 |
| Turck DWE draw-wire (reference) | DWE-10000-120 | 10 m industrial draw-wire | 2,070 | EUR | 2026-11-07 | https://www.turck.com/de/en/shop/sensors/linear-position-sensors/100049466 | confirmed (listed price), snippet |
| Micro-Epsilon WPS-MK30/MK46 OEM low-cost | WPS-…-MK30 | low-cost OEM draw-wire for series integration | not published | – | 2026-11-07 | https://www.micro-epsilon.com/newsroom/press/article/draw-wire-sensors-for-series-integration-oem/ | estimate (quote-only, volume) |

**Notes on industrial suitability**
- **Ice and dirt.** Draw-wire sensors on hooklifts and compactors are exposed to ice, dirt and impact, and the wire freezing is a known failure mode at −30 °C.
- **Better alternatives for arm position.**
  - A sealed **inclinometer** on the arm (IP67, Modbus/CANopen, ~€100–350, see §8).
  - A cylinder with an integrated magnetostrictive sensor. This is OEM-only and has a high retrofit cost.
- **If draw-wire is used.** Choose an IP65+ stainless-wire type with a 4–20 mA or CANopen output and a protective housing.
- **Budget.** **€300–600** for an industrial unit.

---

## 6. Motor current / energy metering

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| YHDC SCT-013-030 split-core CT | SCT-013-030 | 30 A, 1 V output (internal burden), 3.5 mm jack, hobby grade, not IP rated | 8.95 ex GST (9.85 inc) | AUD | 2026-11-07 | https://core-electronics.com.au/non-invasive-ac-current-sensor-30a-max-seeed-studio.html.md | confirmed (listed price) |
| PowerUC SCT013-30-333 (DigiKey) | SCT013-30-333 | 30 A, 333 mV output | 4.97 | EUR | 2026-11-07 | https://www.digikey.de/en/products/detail/poweruc-electronics/SCT013-30-333/25966686 | confirmed (listed price), snippet |
| Magnelab split-core CT | SCT-0400-030 / SCT-0250-030 | 30 A, 333 mV, UL-listed, revenue-grade accuracy ~1 % [verify] | not captured (Kele listing) | – | 2026-11-07 | https://www.kele.com/product/power-monitoring-and-protection/current-transformers/magnelab/sct-0400-030 | estimate (quote / not captured) |
| Eastron SDM630 Modbus V2 (MID) | SDM630-Modbus-MID V2 | 3-phase, 100 A direct, RS485 Modbus RTU, MID class B | 90.99 ex VAT (110.10 inc) – Ropere; 127.57 inc – Daycomp; ~60 used eBay | EUR | 2026-11-07 | https://www.ropere.com/p/eastron-sdm630-modbus-mid-v2-modbus-three-phase-electricity-meter-100a | confirmed (listed price) |
| Carlo Gavazzi EM24 DIN | EM24DINAV93XO2X | 3-phase, 65 A direct, Modbus RTU, class 1 / B | 281.26 ex VAT (RS IE); 304.04 ex VAT (Farnell IE) | EUR | 2026-11-07 | https://ie.rs-online.com/web/p/energy-meters/2864874 | confirmed (listed price) |

**Notes on industrial suitability**
- **Use case.** Compactor motor or pump energy per press cycle is a cheap *proxy* for compaction effort and fill: current rises as the container fills.
- **Recommended meter.** A DIN-rail Modbus meter such as the SDM630 at about €90–130 is the cheapest robust way to get per-phase current, power and energy in an electrical cabinet. It is MID-certified and logs to the gateway over RS485.
- **CT-only option.** SCT-013 CTs suit only prototypes: they have no IP rating and an exposed jack. Use DIN or enclosed CTs for products.
- **Electrical safety.** Installing in a compactor's 400 V cabinet requires a qualified electrician (see §12).

---

## 7. Distance / fill-level sensors

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| MaxBotix HRXL-MaxSonar-WRMT | MB7389-100 | ultrasonic 0.3–5 m, 1 mm resolution, IP67, filtering for clutter, −40…+65 °C [verify] | 109.95 (MaxBotix) / 82.00 ex VAT (exp-tech, -100 variant) | USD / EUR | 2026-11-07 | https://maxbotix.com/products/mb7389 ; https://exp-tech.de/en/products/maxbotix-ultrasonic-precision-rangefinder-mb7389-hrxl-maxsonar-wrmt | confirmed (listed price) |
| Benewake TF02-Pro | TF02-Pro IP65 | LED ToF 0.1–40 m (lower on dark targets), IP65, UART/I²C, −20…+60 °C [verify] | 102.48 inc VAT (RobotShop EU) / 91.64 USD | EUR / USD | 2026-11-07 | https://eu.robotshop.com/products/benewake-tf02-pro-lidar-led-rangefinder-ip65-40m | confirmed (listed price) |
| Garmin LIDAR-Lite v4 LED | 010-02022-00 [verify] | 10 m, I²C/ANT, **no IP rating** (board level) | 119.95 | USD | 2026-11-07 | https://www.sparkfun.com/garmin-lidar-lite-v4-led-distance-measurement-sensor.html | confirmed (listed price) |
| VEGA VEGAPULS C 11 | PSC11 | 80 GHz radar, 0–8/10 m, ±5 mm (per VEGA page) / ±2 mm per datasheet [verify], 4–20 mA, IP66/IP68, −40…+60 °C | **576.00** (base, 1 pc; −10 % from 5 pcs). Earlier search snippet: 550 | EUR | 2026-11-07 | https://www.vega.com/en-de/products/product-catalog/level/radar/vegapuls-c-11 | confirmed (listed price, manufacturer web shop) |
| VEGA VEGAPULS C 21 | PSC21 | 80 GHz radar, 15 m, 4–20 mA + Modbus/SDI-12 variant, IP66/IP68 | 1,197 (US base price) | USD | 2026-11-07 | https://www.vega.com/en-us/company/vega-americas/radar-sensors-for-liquid-level-measurement | confirmed (listed price), snippet |
| Pepperl+Fuchs / Banner industrial ultrasonic | e.g. UB2000-F42-… | industrial M30/F42, IP67 | not captured | – | 2026-11-07 | – | estimate (not found; typically €250–500, assumption) |

**Notes on industrial suitability**
- **Inside a compactor container or chamber,** the sensor faces dust, condensation, frost and splashing. Radar (VEGA C 11) is the only option here unaffected by dust, fog, frost and temperature gradients, and it is still affordable: €576 list from VEGA.
- **Ultrasonic (MB7389).** Cheap and IP67, but it suffers from soft or angled targets (bags), temperature gradients and ice on the transducer.
- **LED ToF (TF02-Pro).** IP65 only, and the window fogs or dirties. It is good for prototyping only.
- **Garmin LIDAR-Lite.** Not outdoor-capable without a custom enclosure.

---

## 8. Accelerometers / IMU / inclinometers; temperature & humidity

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| WitMotion HWT901B | HWT901B-485 | 9-axis AHRS (MPU9250-class), IP67, RS485/RS232/TTL | 85.00 (sold out) | USD | 2026-11-07 | https://rcdrone.top/products/witmotion-hwt901b-accelerometer-with-air-pressure | confirmed (listed price) |
| WitMotion WT901 (board/module, no IP) | WT901 / WT901C-485 | 9-axis, TTL / RS485 | 40–48 | USD | 2026-11-07 | https://www.robotshop.com/products/witmotion-witmotion-wt901blecl-mpu9250-high-precision-9-axis-gyroscope-accelerometer-magnetometer-3-axis-bluetooth-ahrs-imu-sensor-arduino | confirmed (listed price) |
| Elkome-listed MEMS tilt sensor, RS485, IP67 | (see shop) | IP67, −40…+85 °C, RS485 | 333.00 | EUR | 2026-11-07 | https://shop.elkome.com/en/sensors/tilt-sensors/mems | confirmed (listed price), snippet (Finnish distributor) |
| RION SCA126T-485 dual-axis inclinometer | SCA126T | IP67, RS232/RS485 | "93" (currency unstated) | ? | 2026-11-07 | https://rioninclinometer.company.frbiz.com/p114404822-sca116t-sca126t-dual-axis-inclinometer-with-rs232-rs485-output-ip67-protection.html | estimate (currency unclear) |
| POSITAL TILTIX | ACS-360-1-M100-VE2-PM | 1-axis 360°, Modbus RTU, IP67 | not shown | – | 2026-11-07 | https://www.posital.com/en/products/inclinometers/tiltix-product-finder/ACS-360-1-M100-VE2-PM/124644501/detail.php | estimate (quote-only) |
| SHT40 RS485 Modbus probe (EU seller) | – | Sensirion SHT40, RS485 Modbus RTU, 2 m cable, "waterproof" (IP not specified) | 19.60 inc VAT | EUR | 2026-11-07 | https://www.neven7.eu/p/sht40-rs485-2m-digital-humidity-temperature-sensor | confirmed (listed price) |
| SHT40 RS485 Modbus module | – | SHT40, Modbus RTU | 13.90 (11.82 qty) | CAD | 2026-11-07 | https://universal-solder.ca/product/rs485-modbus-temperature-humidity-sensor-high-accuracy-sht40/ | confirmed (listed price) |
| Sensirion SHT45 bare sensor | SHT45-AD1B-R2 | ±1 %RH / ±0.1 °C, I²C, PTFE membrane option (-AD1F) | 4.16–5.99 | USD | 2026-11-07 | https://www.findchips.com/search/SHT45 | confirmed (listed price, distributor aggregate) |

**Notes on industrial suitability**
- **Low-cost path.** For arm-angle compensation of the pressure-based estimate (§4), a sealed IP67 RS485 or CANopen inclinometer is needed. Cheap WitMotion IP67 units cost about USD 85; industrial POSITAL/Elkome units cost about €300+.
- **Temperature/humidity.** Use a stainless or PTFE-filter probe (SHT4x) mounted in a vented IP67 box. SHT4x chips are cheap; the enclosure, membrane and EMC design are the real cost.
- **Use of temperature data.** Measuring temperature is useful for load-cell or strain zero-drift compensation.

---

## 9. Weighing electronics: amplifiers, indicators, transmitters, ADCs, junction boxes

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| Laumas TLB weight transmitter (DIN rail) | TLB / TLB4 (RS485/Modbus, analog) | 24-bit, 4 load cells, Modbus RTU, 4–20 mA/0–10 V out, OIML R76 approvable variants [verify] | 21,000 (≈ €210) – Indian distributor | INR | 2026-11-07 | https://www.indiamart.com/innovative-engineeringsolutions/laumas-weight-transmitter.html | confirmed (listed price), non-EU |
| Laumas TLE analog transmitter (AutomationDirect) | TLE | load-cell to 4–20 mA/0–10 V DIN transmitter | 210 | USD | 2026-11-07 | https://cdn.automationdirect.com/static/catalog/images/product-pdf/Force-Measurement-Devices.pdf | confirmed (listed price), snippet |
| Dini Argeo DGT1S transmitter/indicator (used) | DGT1S / DGT1SAN | DIN, RS485, analog out, 12–24 VDC | 199 (used, eBay.de) | EUR | 2026-11-07 | https://www.ebay.de/itm/316782046811 | confirmed (listed price, used) |
| Rice Lake 482 Plus indicator | 482 Plus LCD | NTEP / Measurement Canada legal-for-trade [verify OIML/MID] | 770.25–838.50 | USD | 2026-11-07 | https://www.scalesgalore.com/M1/Rice-Lake-482-Plus-LCD-Legend-Series-Digital-Weight-Indicator-with-Quick-Connect-px46262.cfm | confirmed (listed price) |
| Dini Argeo DFWLB / DFWLI / DGT20I (IP68 stainless) | DFWLB, DFWLI, DGT20I | IP68, CE-M approvable OIML R76 / EN 45501 (DGT20I: R76 + R51/R61) | not published (dealer "net price") | – | 2026-11-07 | https://www.diniargeo.com/dini-product/dgt20i-ip68-stainless-steel-weight-transmitter-indicator/?print=true | estimate (quote-only; typical €300–700, assumption) |
| Laumas WINOX-G (IP68 stainless) | WINOX-G | OIML R76:2006 class III 10000 d, IP68 | not published | – | 2026-11-07 | https://www.laumas.com/en/product/winox-g-stainless-steel-ip68-weight-indicator-for-weighing-and-batching/?atLng=FR | estimate (quote-only) |
| HBK ClipX / PW-series, Flintec FT-11, Mettler IND series | ClipX BM40, FT-11, IND570 | industrial DIN transmitters/indicators | not found | – | 2026-11-07 | – | estimate (quote-only; ClipX/FT-11 typically €500–1,000, assumption) |
| SparkFun HX711 breakout | SEN-13879 | 24-bit, 10/80 SPS, 2 ch, single 2.6–5.5 V | 4.95 (4.21 @100) | USD | 2026-11-07 | https://www.sparkfun.com/products/13879 | confirmed (listed price) |
| SparkFun Qwiic Scale NAU7802 | SEN-15242 | 24-bit, I²C, PGA, up to 320 SPS | 5.95 (5.06 @100) | USD | 2026-11-07 | https://www.sparkfun.com/sparkfun-qwiic-scale-nau7802.html | confirmed (listed price) |
| ADS1232 module (CJMCU) / bare IC | CJMCU-1232 / ADS1232IPWR | 24-bit ΔΣ, low-noise PGA, 10/80 SPS, 50/60 Hz rejection | module 8.14; IC 2.58 (1 pc, LCSC) | USD | 2026-11-07 | https://electropeak.com/cjmcu-ads1232-24-bit-analog-to-digital-converter ; https://www.lcsc.com/product-image/C27919.html | confirmed (listed price) |
| Transcell JB-SS-4 stainless 4-cell junction box | JB-SS-4 | 4 cells, signal trim | 152.89 (MSRP 185) | USD | 2026-11-07 | https://scalesplus.com/transcell-jb-ss-4-stainless-steel-signal-trim-junction-box-102000241 | confirmed (listed price) |
| ANYLOAD J04ES/J04SS-E stainless J-box | J04SS-E | 4 cells, IP65 (sibling model) | 162 | USD | 2026-11-07 | https://tacunasystems.com/products/summing-junctions/anyload-j04es-j04ss-stainless-steel-junction-box/ | confirmed (listed price) |
| Dini Argeo JB4QIP69K | JB4QIP69K | AISI 304, IP68/IP69K, 4 cells, equalising | not published | – | 2026-11-07 | https://www.diniargeo.com/dini-product/jb4qip69k-equalized-junction-box-with-4-inputs-in-stainless-steel-with-ip68-ip69k-protection/?print=true | estimate (quote-only) |

**Notes on industrial suitability (why hobby ADCs are not deployment-ready)**
- **The chips themselves are not the problem.** HX711, NAU7802 and ADS1232 are fine 24-bit bridge ADCs (the ADS1232 is used in commercial scales).
- **What hobby breakouts lack:**
  - EMC/ESD/surge protection on the bridge lines (vehicle 24 V, alternator load dump, welding on the chassis).
  - 6-wire sense, so cable resistance and temperature changes cause span error.
  - Ratiometric excitation and filtering.
  - Conformal coating and an IP enclosure.
  - Validated temperature drift (HX711 zero drift and its 10/80 SPS fixed rates are poor for dynamic vehicle weighing).
  - Calibration and seal mechanisms (no legal-for-trade audit trail).
- **Product path.** Either use an industrial DIN transmitter (Laumas TLB, Dini DGT1S, HBK ClipX: ~€200–700) with Modbus into the gateway, or design a custom board around the ADS1232 or AD7190 with proper protection.
- **Legal for trade.** Billing by weight requires an EU/MID (2014/31/EU NAWI) type-approved indicator (OIML R76 / EN 45501 certificate) plus initial verification of the complete instrument; see §12.
- **Junction boxes.** Use stainless IP68 (Dini JB4QIP69K) for washdown. The common USD 150 boxes are IP65–IP67.

---

## 10. IoT / edge gateways and PLCs

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| Teltonika TRB245 | TRB245000000 | LTE Cat 4 gateway, RS232/RS485, 1 analog input **0–30 V (voltage only)**, DI/DO, −40…+75 °C | 114.49 inc VAT (aio.lv, valid to 07/2026); 141.13 ex VAT (xpatit.gr); 224.65 (partco.fi, on request) | EUR | 2026-11-07 | https://aio.lv/en/product--teltonika-trb245000000--3511866 ; https://www.partco.fi/en/iot/iiot/23900-trb245.html | confirmed (listed price) |
| Teltonika RUT956 | RUT956200000 (EU) / RUT956400V00 | LTE Cat 4 router, Wi-Fi, GNSS, RS232/RS485, analog input 0–24 V **with 4–20 mA capability (external shunt resistor)**, −40…+75 °C | 219.56 ex VAT (261.28 inc) | EUR | 2026-11-07 | https://industry-electronics.com/teltonika/rut956200000-router-rut956-lte-modem-wlan-lieske_1385091.htm | confirmed (listed price) |
| Siemens LOGO! 8.4 12/24RCE | 6ED1052-1MD08-0BA2 | 8 DI (4 usable as 0–10 V AI), 4 relay DO, Ethernet; 4–20 mA needs AM2 module | 110.88 (Gabby) / 150.00 (RS AT) / 161.58 inc VAT (Bürklin) | EUR | 2026-11-07 | https://at.rs-online.com/web/p/sps-zentralbaugruppen/2825512 | confirmed (listed price) |
| Moxa ioLogik E1242(-T) | ioLogik E1242 / E1242-T | Ethernet remote I/O, 4 AI (0–10 V / 0/4–20 mA), 4 DI, 4 DIO, Modbus TCP; -T = −40…+75 °C | 326 net (E1242, Elmark); 487 ex VAT (E1242-T, Lieske) | EUR | 2026-11-07 | https://elmark-automation.com/shop/moxa/iologik-e1242 | confirmed (listed price) |
| Industrial Shields ESP32 PLC 14 | ESP32 PLC 14 | ESP32, DIN, 24 V, analog inputs selectable 4–20 mA or 0–10 V, RS485, Wi-Fi/BLE | from 109 (PLC 21: 239; PLC 58: 379) | EUR | 2026-11-07 | https://www.industrialshields.com/esp32-plc-14-launch-lp | confirmed (listed price) |
| NORVI IIOT-AE02-I | NORVI-IIOT-AE02-I | ESP32 DIN controller, 6× 4–20 mA AI | 240.76 | USD | 2026-11-07 | https://shop.norvi.lk/products/norvi-iiot-ae02-i | confirmed (listed price) |
| Olimex ESP32-POE-ISO | ESP32-POE-ISO | ESP32 + isolated PoE Ethernet board (no enclosure, no AI conditioning); -IND variant for −40 °C | 24.95 (Olimex, 1 pc) / 29.00 net (TME) | EUR | 2026-11-07 | https://www.olimex.com/Products/IoT/ESP32/ESP32-POE-ISO/ | confirmed (listed price) |

**Notes on industrial suitability**
- **Vehicle or container-side, cheapest credible stack:**
  - Teltonika RUT956: LTE, GNSS, RS485 for a Modbus weighing transmitter and energy meter, plus one 4–20 mA input. About €220 ex VAT.
  - Or TRB245 plus an RS485 transmitter: about €115–140.
- **Fixed compactors.** A Moxa E1242-T with any LTE router, or an Industrial Shields ESP32 PLC (CE, DIN, 4–20 mA, €109+), is credible.
- **Bare ESP32 boards (Olimex).** They need an enclosure, isolation and a 24 V/vehicle-transient front end before field use.
- **Siemens LOGO!** Robust, but it adds cost for analog and LTE (CMR2020 module), and its integration is weaker than Teltonika's.

---

## 11. Complete systems – reference prices

| Product | Part no. | Key specs | Price | Currency | Date | URL | Price status |
|---|---|---|---|---|---|---|---|
| WeDi container scale for K3 / roll-off containers | BKSB 15000 kit + ramps | 15 t, 2 kg readability, 4× K30S 5 t cells, JBB-04 junction box, BWI indicator, ramps/beams; trade approval not stated | 4,800 ex VAT (header) / 5,620 ex VAT (text) | EUR | listing upd. 2024-06-18 | https://www.machineseeker.ie/firma+wedi+gmbh-containerwaage/i-5910742 | confirmed (listed price; conflicting figures) |
| Rice Lake TradeRoute HL legal-for-trade onboard hooklift/roll-off scale | TradeRoute HL | legal-for-trade (NTEP), up to 60,000 lb | 18,480 (system); components e.g. kiosk control box 5,350, in-cab install item 4,150 | USD | 2026-11-07 | https://selletonscales.com/products/traderoute-hl-series-onboard-weighing-system | confirmed (listed price) |
| Pfreundt hook-lift scale (WK60 family) | – | EU-type-approved onboard hooklift scale (trade-approved variants) [verify] | "depends on vehicle type, equipment…" – not published | – | 2026-11-07 | https://www.pfreundt.de/en/products/hook-lift-scale/ | estimate (quote-only) |
| Tamtron One Power truck / hooklift scale | – | Finnish OEM; trade-approved onboard weighing | not published | – | 2026-11-07 | https://tamtrongroup.com/en/product/one-power-truck-on-board-scale | estimate (quote-only) |
| Loadrite E2750 hook-lift scale | E2750 | dealer-sold, most hooklift makes | not published | – | 2026-11-07 | https://www.goloadrite.com/e2750-hook | estimate (quote-only) |
| Loadsense hooklift onboard system | – | load cells between chassis and hooklift frame, or air-bag sensors | not published | – | 2026-11-07 | https://loadsensescales.com/product/onboard-weighing-system-for-hook-lift-waste-trucks-and-trailers/ | estimate (quote-only) |
| Generic installed load-cell onboard system (vendor table) | – | full load-cell system, installed | 10,000–15,000 (high end) | USD | 2026-11-07 | https://szlmi.com/onboard-weighing-system-vs-load-indicator-vs-load-scale-which-solves-your-fleets-weight-problem-in-2026/ | estimate (vendor-compiled range) |
| Rice Lake RL1800 complete weigh-module kit (4 cells, SS) | RL1800 5,000 lb LE SS | cells + modules + J-box + cable | 4,650 | USD | 2026-11-07 | https://www.ricelake.com/products/rl1800-series-with-mlc-coated-load-cell-weigh-module-kit?print=true | confirmed (listed price), snippet |

**Notes**
- **Market anchor:** legal-for-trade onboard hooklift systems sell at **≈ €10–20 k installed**. Non-trade static container or pit-frame scales sell at **≈ €5–6 k hardware ex VAT** before installation.
- **Not found:** axle weigh pad prices were not found in this session. They are typically quote-only; treat any figure as an assumption.
- **Finnish market:** Tamtron, a Finnish company, is the incumbent for onboard trade-approved weighing in Finland. Pricing is quote-only.

---

## 12. Installation labour, calibration and verification (Finland/EU)

| Item | Evidence | Figure | Currency | Date | URL | Status |
|---|---|---|---|---|---|---|
| Scale service technician hourly rate | US industry analogy ("mechanics start at $150/h, scale service similar") | ~150 / h | USD | 2026-11-07 | https://www.americanscaleus.com/knowledge-center/scale-service-cost-guide | estimate (US analogy) |
| Load-cell replacement + calibration (force gauge, bench) | Mark-10 price list | 495 | USD | 2026-11-07 | https://mark-10.com/?p=1223 | confirmed but not comparable (bench instrument) |
| Scale calibration flat rate (own brand, AU) | Scintex | 295 inc GST | AUD | 2026-11-07 | https://www.scintex.com.au/pages/scale-calibration-service | confirmed but not comparable |
| Finnish legal verification (vakaus/varmennus) of NAWI | Kiwa Tarkastus Oy is one of 4 approved bodies; Tukes supervises; periodic verification of scales every 3 years; **no public price list found** | n/a | – | 2026-11-07 | https://www.kiwa.com/fi/fi/palvelutyyppi/kalibrointi-ja-varmennus/mittauslaitteiden-varmennus/ | quote-only |
| EU onboard installation item (Rice Lake TradeRoute in-cab install) | list item | 4,150 | USD | 2026-11-07 | https://www.ricelake.com/products/traderoute-hl-series-legal-for-trade-onboard-weighing-system?print=true | confirmed (listed price) |

**Working assumptions.** No public Finnish or EU figure was found, so these must be validated with Kiwa, Lahti Precision, Tamtron or a local scale service company:
- **Load-cell retrofit installation on a compactor or hooklift subframe:** 1–2 technician-days (fabrication, mounting plates, welding, cabling). At €70–95/h in Finland that is **€600–1,500 per unit**, plus fabricated steel parts at €300–1,000.
- **Calibration with certified test weights:**
  - Typically €400–1,000 per visit, plus test-weight truck or transport. Test-weight logistics dominate for 3–10 t ranges.
  - Substitution with a reference-weighed container is cheaper but less accurate.
- **Legal initial or periodic verification by a notified or approved body:** €300–800 per instrument visit plus travel. Periodic re-verification is required every 3 years in Finland.
- **Electrician for energy meter / CT install in a 400 V cabinet:** 1–2 h, about €100–200.

---

## Gaps and caveats
- **PDFs not read.** Zemic H8C and Brecknell price-list PDFs could not be parsed. The H8C and HM8 prices come from search snippets of the Brecknell list, which is undated and may be old.
- **Spec tags.** OIML C3 combined-error, creep and TC values per cell should be pulled from the datasheets before final selection. Typical C3 datasheet values are combined error ≤ ±0.02 % RO, creep ≤ ±0.024 %/30 min, TC zero ≤ ±0.0023–0.004 %/K, TC span ≤ ±0.001 %/K. These are indicative only.
- **Cheap 400 bar transducer.** No priced 0–400 bar, 0.5–4.5 V Chinese transducer was verified. The "~€30" figure remains an **unverified estimate**.
- **Quote-only items:** HBK (SLB700A, ClipX), Mettler Toledo, Flintec FT-11, LCM Systems, Strainsert (real), Pfreundt, Tamtron and Loadrite.
