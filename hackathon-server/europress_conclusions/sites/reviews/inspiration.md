# Design inspiration: SMART Verified Weight (Page A product site, Page B business-plan explainer)

Checked 2026-11-06. Every URL returned HTTP 200. Patterns come from page text via fetch, so visual styling is unverified. Where a page was JS-only or gated, I say so. Borrow behaviours, not looks or assets. 403 to bots, excluded: Compology, Augury, Normative. Palantir Foundry fetch failed.

## Sites

**Greyparrot** https://www.greyparrot.ai (A, B). AI waste analytics for recycling plants.
- Scenario simulator at /ai-facility-simulator: three problems, "8 minutes", "no commitment", KPIs move as you act (gated form, interior not seen).
- Metric-first testimonial cards, e.g. "30% to 20% value lost to residue".
- Looping dashboard previews in product cards.

**Sensoneo** https://www.sensoneo.com (A). Smart-bin sensors.
- Stat strip straight under the hero (55K+ sensors, 90+ countries).
- Case cards open with the number.
- Only stock photos and no product UI, so a real dashboard in our hero sets us apart.

**Nordsense** https://nordsense.com (A). Waste IoT.
- Three-card "how it works" flow.
- Tabbed cases with three "Project Findings" figures each.
- Also shows no product UI.

**Tulip** https://www.tulip.co (A). Frontline-ops platform.
- Tab panel with numbered use cases beside an app preview.
- Outcome arrows on testimonials (down 66% defects).
- Paired CTAs "Book a Demo" and "Take a Tour".

**Watershed** https://watershed.com (A). Carbon accounting.
- "See how every number was calculated" plus data lineage.
- Stage cards (Collect, Clean, Map, Analyze, Report), each with a UI state such as an anomaly warning.
- Built-in human review.

**Climatiq** https://www.climatiq.io (A). Emissions data API.
- Each result breaks down into stages, assumptions and emission factors.
- Named dataset chips link to sources.
- Check/cross comparison table.

**Tradeshift** https://tradeshift.com (A). E-invoicing and AP.
- Six numbered steps ending in "compliance and auditing" and "real-time insights".
- Precise claims ("96.9% no manual touch").
- Deadline-led hero.

**Modern Treasury** https://www.moderntreasury.com (A). Payment operations.
- Four-stage lifecycle with reconciliation as the last stage.
- Real JSON request and response used as the demo.

**Vanta Trust Center** https://www.vanta.com/products/trust-center (A). Compliance evidence.
- Live control status.
- Gated document access.
- Filters by product or region.

**Tremor** https://www.tremor.so and **Evidence** https://evidence.dev (A). Dashboard blocks.
- KPI card with delta badge.
- Donut with legend rows.
- Ranked bar list.
- Status-segment strip.
- Labelled mockups so each UI part maps to a feature.

**Linear** https://linear.app (A, B). Marketing page.
- Full-width real product mockup under the hero.
- "Fig 0.1" numbered captions and eyebrow labels.
- Dated changelog list.

**Vaisala** https://www.vaisala.com/en (A). Finnish measurement company.
- Frames the chain as "reliable measurements to trustworthy data".
- Numeric counters under the hero.
- Never states accuracy or uncertainty. We can.

**Fortum** https://www.fortum.com and **Kone** https://www.kone.com/global/en.html (A). Nordic corporate.
- Fortum: units and qualifiers in the label, "~" for approximations, block titled "in numbers 2025".
- Kone: numbered breadcrumbs, three-column figures with line icons, calm card grid.

**Climate TRACE** https://climatetrace.org (A, B). Emissions data.
- Aggregate view versus single-asset view.
- Versioned releases ("release 5.12.0, data through Aug 2026").
- Methodology and open-data links.
- No uncertainty shown. We can add it.

**Our World in Data** https://ourworldindata.org (B). Data explainers.
- Source and licence line under every chart.
- Question-style headings.
- "Explore the data" link from static chart to interactive one.

**R2D3 Visual intro to ML** https://r2d3.us/visual-intro-to-machine-learning-part-1/ and **The Pudding** https://pudding.cool (B).
- R2D3: sticky graphic with step text. The same data points re-encode at each step and an accuracy figure climbs.
- Pudding (index page only read): visual data stories, typed filters.

**Bartosz Ciechanowski** https://ciechanow.ski (B). Interactive essays.
- One layer added per step.
- Sliders.
- Real/exaggerated scale toggle.
- Live plots.
- Ghost trails.

**Nicky Case** https://ncase.me and https://ncase.me/trust/ (B). Explorable explanations.
- Index page only read; the Trust page renders by JS.
- From prior knowledge: short chapters, each ending in a tweakable sandbox with a reset button.

**Stripe pricing** https://stripe.com/en-ee/pricing and **Wise pricing** https://wise.com/gb/pricing/ (B). Pricing pages.
- Stripe: sticky anchor bar, cards of rate, unit and small-print conditions, Standard/Custom split.
- Wise: "Fees at a glance", free-up-to-threshold then percentage on excess.
- Neither has a live calculator.

**Supabase pricing** https://supabase.com/pricing and **Datadog pricing** https://www.datadoghq.com/pricing/ (B).
- Supabase: worked example ($25 plan, plus $10 per project, minus $10 credit = $35), overage rates, spend-cap toggle.
- Datadog: tier selectors and units spelled out ("per host per month"), footnotes define the units.

**Ellen MacArthur circular economy diagram** https://www.ellenmacarthurfoundation.org/circular-economy-diagram (B).
- Two colour-coded loops and "Dig deeper" cards.
- Downloadable PNG/PDF.
- The diagram is a static image, so interactivity would be ours to add.

## Top 8 patterns for Page A

Brand: navy #000d61, mint #54dea9 (CTA and "reconciled" only), ice #e0f1f5 panels, Archivo headings, Open Sans body.

1. Put a product card in the hero, not a photo: a large verified weight (Archivo 800, navy) over a three-source strip (compactor estimate, weighbridge ticket, invoice). The mint CTA "Explore the demo" sits next to it.
2. Write every estimate as value plus band: "12.4 t ± 0.3", with a thin range bar (ice band, navy tick). Put units and qualifiers in the label, and use "~" for approximations.
3. Give every figure a provenance chip (pill, ice fill, navy 1px border) with source, timestamp and a "how calculated" drawer. Mint dot means reconciled, outline means pending, and one amber is reserved for flagged variance.
4. Offer scenario buttons in the embedded demo ("Matched", "Short-weight invoice", "Missing ticket") that swap deterministic JSON. No form gate, and a visible "8-minute tour" label. Pair the mint "Open demo" button with an outline "60-second tour" button.
5. Show cause attribution as a ranked bar list with a confidence value per row (Tremor-style) and a 30-day status strip of day cells coloured by reconciliation state.
6. Render recommended actions as cards with Approve / Edit / Dismiss and an audit-log line ("Approved by J. Virtanen, 14:02"), so human approval stays visible.
7. Explain how it works as a numbered, sticky stepper: Measure, Match ticket, Match invoice, Attribute cause, Approve. Each step shows a small UI state, not an icon.
8. Place a proof band right under the hero with three big numerals, qualified labels and sources. Label demo data "illustrative" and cite epsmart.fi figures with their source. Use Nordic restraint (whitespace, no stock photography).

## Top 8 patterns for Page B

1. Use a sticky stage on the right in an ice panel and scrolling step text on the left. The same dot-per-tonne marks morph through each stage (IntersectionObserver, mint highlight on the active step, a reduced-motion fallback).
2. Build the value chain up one layer per scroll step (Europress, customer, hauler, weighbridge, invoice, verifier) with nodes that never move.
3. Draw the value chain as a loop diagram with three flow types (material, money, data) in distinct stroke styles. Node click opens a side panel (inputs, outputs, owner). Include a table fallback and PNG export.
4. Make the pricing calculator a set of sliders (compactors, tonnes per month, disputed share) with an itemised live result. Show the arithmetic line by line, state units ("per compactor per month") and recompute across tiers. Mint highlights the total only.
5. Lay fees out as "at a glance" rows (label, rate, unit, condition in small print). Add a sticky anchor bar: Value chain, Pricing, Roadmap.
6. Add a "without / with verification" toggle that flips the P&L waterfall, plus a reset button, so one assumption changes at a time.
7. Put a one-line source, assumption and date under every chart. Use question headings ("What does a disputed tonne cost?") and link each static chart to the calculator.
8. Present the roadmap as Now / Next / Later lanes with dated milestones, exit criteria, "Fig 3.1" captions and eyebrow labels. Use expandable cards and no fake percent-complete.
