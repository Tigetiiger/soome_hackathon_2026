# Business findings, explained in plain language

**Europress × Since AI Hackathon 2026**, 7 November 2026

This is a reader-friendly version of `04_business_findings_and_decisions.md`. It contains the same findings and decisions, but explains the background and the terms as it goes. You don't need to know the waste industry, the hackathon or any data science to follow it.

> **One important warning before you start.** Every number that comes from "the data" was computed on a **practice dataset** that Europress made up for the competition (52 imaginary customers, imaginary operators, imaginary prices). These numbers show what the method *can* find. They are **not real savings** and must be replaced with real data in a pilot.

---

## Contents

- [The story in one minute](#0-the-story-in-one-minute)
- [Words you will need](#words-you-will-need)
- [What Europress asked us to do](#1-what-europress-asked-us-to-do)
- [Who Europress is](#2-who-europress-is)
- [The market and the competition](#3-the-market-and-the-competition)
- [The customer's problem, and what the data shows](#4-the-customers-problem-and-what-the-data-shows)
- [What we sell, and what we deliberately don't](#5-what-we-sell-and-what-we-deliberately-dont)
- [How it makes money](#6-how-it-makes-money)
- [Does it pay off?](#7-does-it-pay-off)
- [The launch plan, with stop signs](#8-the-launch-plan-with-stop-signs)
- [Keeping waste operators on side](#9-keeping-waste-operators-on-side)
- [Risks and how we handle them](#10-risks-and-how-we-handle-them)
- [How we would measure success](#11-how-we-would-measure-success)
- [Every decision we made, and why](#12-every-decision-we-made-and-why)
- [Questions we still need Europress to answer](#13-questions-we-still-need-europress-to-answer)

---

## 0. The story in one minute

- **Europress** makes waste **compactors**: machines that press waste into a container so it takes less space. Shops, hotels, factories and property managers have them on site.
- A separate company, the **waste operator**, comes with a truck, takes the container away, empties it and bills the customer. Most of the bill is calculated **per tonne** of waste.
- The problem is that **the customer never sees the weight**. The weight is measured by the operator, and the operator is the one paid per tonne. The customer has no easy way to check whether the bill is right or whether the price is fair.
- Europress's connected service, **SMART**, already knows how *full* each machine is and when it should be emptied. It does **not** know how *heavy* the waste is. Europress told us that weight is the missing piece: "every invoice, every contract, everything is about weight."
- **Our proposal:** use the Europress machines to give the customer an **independent estimate of the weight** (mostly through software, with almost no new hardware), and a **customer dashboard** that turns this into plain answers: what you pay, whether it looks right, and how you could save money.
- **The business point:** the add-on alone earns modest money. Its real value to Europress is that it makes customers **more likely to buy SMART and to keep their service contracts**, which is where Europress makes its profit.
- **The diplomatic point:** waste operators are also Europress customers. The product must be **neutral**. It says "this needs a second look", never "you were cheated".

---

## Words you will need

| Term | What it means here |
|---|---|
| **Compactor** | A machine that crushes and presses waste into a container. Europress's main product. |
| **Baler** | A machine that presses material such as cardboard into tight bales. |
| **Waste operator** (or just "operator", "hauler") | The company that collects the waste with trucks and bills the customer. Not Europress. |
| **Lift / pickup / emptying** | One visit where the operator takes the container away to empty it. |
| **Weighbridge** | A large scale that a truck drives onto. The operator uses it to weigh the waste. |
| **Ticket** (weighbridge ticket) | The slip that records that weight. Some operators share it with the customer, some don't. |
| **Tare** | The weight of the empty container. It is subtracted from the total to get the waste weight. If the stored tare is out of date, the waste weight comes out wrong. |
| **Side waste** | Extra bags or items left next to the container that the operator also takes and weighs. |
| **€/t** | Price per tonne of waste. |
| **SMART** | Europress's connected service for its machines: remote monitoring, fill-level prediction and support. It has three levels: **Intro**, **Insights** and **Integrated**. Only about 15% of Europress customers use it today. |
| **SMART Center** | Europress's support team who monitor machines remotely. |
| **Fill level** | How full the container is. SMART already measures and predicts this well. |
| **Device weight / virtual scale** | Our estimate of the waste weight, worked out by the compactor itself from data it already has (for example the pressure needed to compact). No scale needed. |
| **Scale platform** | A real scale built under the container. Accurate but expensive. |
| **Device** | One machine (compactor or baler). Prices below are often "per device per month". |
| **Fixed schedule** | The operator empties the container on set days whether it's full or not. The opposite is **on-call**: empty only when needed. |
| **Lease** | Renting a machine for a fixed period, typically about 6 years. |
| **Service contract** | The maintenance agreement for the machine. Europress calls this "the real profit". |
| **Tender** | When a contract ends (usually after 3 years), the customer asks several operators for offers and picks one. |
| **pp** (percentage points) | The plain difference between two percentages. Going from 10% to 15% is +5 pp. |
| **Median** | The middle value when you line everything up. Half are above it, half below. It is often more honest than an average when a few big customers skew the numbers. |

**Labels used in this document.** Every claim carries a tag so you know how much to trust it:

- **[T]** Europress said it (Tommi, Europress's representative, at the kick-off or in the Q&A briefing).
- **[F]** Public fact, found online. Sources are listed in `business_sources/agents/company-profile.md` and `business-strategy.md`.
- **[D]** Computed from the practice dataset with made-up prices. **Not real savings.**
- **[E]** Our estimate.
- **[A]** Our assumption, chosen by us so that we can calculate something.

---

## 1. What Europress asked us to do

| What they asked | In other words | Source |
|---|---|---|
| Focus on **weight**. Predicting when a machine is full and planning pickups already work in SMART. | Don't rebuild what they already have. | [T] briefing, at 00:12, 05:10 and 29:00 |
| Always say **for whom**. Pitch it the way you'd pitch it to that customer. | Write for a real buyer, not in general. | [T] 00:19 |
| "**The meat is the business model.**" Say briefly how you get the weight, then spend your effort on the business. | The sensor details matter less than who pays and why. | [T] 20:23 |
| Make it **win-win-win**: good for the customer, the operator and Europress. | Nobody should lose. | [T] 25:20 |
| "We want to be **more than a device manufacturer**." Europress wants to move earlier in the chain, closer to the service and the data, and weight is the key to that. | Europress wants to sell services, not just machines. | [T] 33:10 |
| Get more customers onto SMART. Only **about 15%** use it today. | Growth target. | [T] |

---

## 2. Who Europress is

**The company** [F]
- **Europress Group Oy**, based in Kerava, Finland. Founded in 1977 and family-owned.
- **The Finnish company:** €40.0M revenue in 2025 (up 12% on the year before), €2.47M operating profit (a 6% margin) and 138 employees.
- **The wider group** has subsidiaries in Sweden (118 MSEK revenue), Norway (105 MNOK), Poland (6–8 MPLN) and the Benelux countries. Added together that is about **€61–63M** before internal sales between group companies are removed. This makes Tommi's figure of "about €70M" believable [F/E].

**Leadership** [F]
- The **new CEO, Petri Salermo** (since October 2025), spent 24 years at Lassila & Tikanoja, one of Finland's biggest waste operators.
- The **incoming Chief Commercial Officer, Eljas Tuovinen** (from January 2027), also comes from Lassila & Tikanoja.
- **Why this matters:** the leadership knows waste operators very well, and operators buy Europress machines too. A product that sets out to "catch" operators would not go down well.

**What Europress sells**
- Compactors (models COMBI and DUO) and balers, either sold outright or leased. Leases typically run about 6 years [T].
- **Service contracts, which Europress calls "the real profit"** [T].
- Retrofit kits that add Europress technology to machines of any brand [F].
- **Scale Solutions:** a scale platform that weighs the container at its four corners, and the Scaletipper X1, which weighs to the nearest 1 kg [F].
- A "waste volume calculator" that estimates weight without a scale [F].

**About SMART**
- About 15 years old, built together with the software company Vincit [F].
- SMART Center offers remote support and says "up to 90% of problems are solved remotely" [F].
- It has a connection for operators' systems (an "operator API") and three levels: Intro, Insights and Integrated [T]. There is no public price list.
- It is sold as a **monthly service fee with nothing to pay up front** [T, briefing 21:44].
- **What Europress publishes about SMART's results** (averages from Europress itself, without error ranges): 40% lower waste costs, 37% fewer emptyings and 58% fuller containers at emptying [F, epsmart.fi].

---

## 3. The market and the competition

**What competitors do** [F]
- The companies that put sensors in waste containers (Compology/RoadRunner, Sensoneo, Enevo, Nordsense, Bramidan BRA-IN, Waste Harmonics) all measure **how full** a container is. **None of them measure weight.**
- **Every existing source of weight belongs to the operator:** either the weighbridge, or scales built into the truck (from makers such as Hyva and RDS).

**The gap we found** [E]
- We found **no company in the Nordic countries that gives the customer an independent weight for each pickup**, one that doesn't belong to the operator.
- Europress already has the machines on site and the sales relationships. The missing part is the software product that turns this into a trusted weight.

**Signs that waste data has value** [F]
- **Greyparrot**, a company that analyses waste with cameras, raised $27M in 2026. It shows that waste data can be sold to other businesses and is accepted by regulators.

**Patents to check** [F]
- The closest existing patents are US11162834 (from BACE, about adding weighing to existing equipment) and US8794135B1. A lawyer should check that we would not infringe them (a "freedom-to-operate" check) before any hardware is built.

**Laws that help us** [F]

Several regulations push companies to know exactly how much waste they produce:

| Rule | What it means in simple terms |
|---|---|
| **CSRD / ESRS E5-5** (EU) | Large companies must report how much waste they produce, by weight, and what happens to it. The EU's "Omnibus" simplification narrowed this to the largest companies. |
| **Waste Framework Directive revision, Directive (EU) 2025/1892** | Food waste must fall by 30% by 2030, which requires measuring it. |
| **PPWR** (EU packaging rules) | Cardboard stays the main material that goes through compactors. |
| **Finnish Waste Act** | Requires waste to be collected in separate streams. |
| **Poland's BDO register** | Polish companies **must report the mass of each type of waste**. A clear need for weight data. |
| **NAWI, 2014/31/EU** (rules on scales used for trade) | A weight from our machine **can be used to check a bill, but not as the official basis for billing**. Only certified scales can do that. This is why we position the product as a "second opinion". |

---

## 4. The customer's problem, and what the data shows

### The problem in Europress's own words [T]

- The customer pays per tonne for a weight **they cannot see**.
- The weight is measured **by the party that is paid per tonne**.
- Customers ask: "Am I paying the right amount? Is the operator doing its best? Would another operator serve me better?"
- Contracts usually run 3 years and then go out to tender, and customers have no good tools to compare operators.

### What we found in the practice data [D]

Remember: imaginary customers and prices. These results show what the approach can reveal, not real money.

| What we looked at | What we found | What it means |
|---|---|---|
| Pickups where the customer can't check the weight today | **26%**. One operator shares none of its weighing tickets. With our machine estimate, **97%** of pickups would have at least one independent weight (74% have a ticket today). | A quarter of pickups are a black box today, and the machine could fill almost all of that gap. |
| Collection spending that can't be linked to a price per tonne | **11%**, or €349k | Money spent without knowing what it bought per tonne. |
| Share of weight-based billing the customer can check | **77% today, 96%** with machine weight | Almost the whole bill becomes checkable. |
| Why the machine's weight and the ticket weight differ by more than 10% | Side waste 34%, an outdated empty-container weight (tare) 30%, several customers' loads weighed together 12%, the **machine's own measurement drifting only about 4%** | Big differences usually have an innocent, explainable cause. **They are not evidence of cheating.** |
| A simple "is this operator biased?" score | It wrongly flags **74%** of operator-region-months as suspicious. Correcting for the known causes cuts its error from 5.5 to 1.2–1.6 percentage points. | A naive check would wrongly accuse operators. The causes must be explained first. |
| How savings are spread between customers | The **average** is about €1,064 per contract per year, but the **median is €0**. The top 5 of all 52 customers hold 54% of the value that can be realised. Among the 20 customers with contract cases, the top 5 hold 75%. | Most customers would gain little. A few large ones gain a lot. This matches Tommi's "80/20" remark. |
| Billing errors that can **only** be found with an independent weight | Only about **€8k in 10 months**, roughly €21 per machine per year | Don't sell this as "we recover overcharging". The money isn't there. |
| Customers on fixed schedules | **30–32%** of pickups were unnecessary, worth about **€2.5–2.7k per machine per year** | A real saving: empty when full, not on a timetable. |
| Changing operator or renegotiating the contract | The best combination of actions saves **7.9%** of costs. Weight makes this possible: +€190 per contract per year where operators don't share tickets. | Weight is the evidence that makes a negotiation or tender possible. |
| Checking weight as well as fill level before ordering a pickup | Correct **96%** of the time it raises a flag, against **5%** for a rule that looks at fill level only | The one case where weight clearly beats fill level on its own. |

### What did *not* work, stated openly [D]

We think it matters to say what we tried and what failed:

- **Wet or contaminated waste can't be detected** by comparing weight with fill level. The results were close to a coin toss (a score of 0.5–0.7, where 0.5 means pure chance). Using density as a clue was right only about 1% of the time.
- **Reducing unnecessary service gains nothing from weight.** SMART's fill-level data already handles that.
- **An accuracy of ±3.3% for each pickup is unrealistic.** 53% of pickups with both measurements differ by more than that. Even the operator's own weighbridge is within ±100 kg on only 78% of pickups.
- **A popular automatic method for spotting unusual data ("isolation forest") was useless here**, scoring 0.10 out of 1 at finding weight gaps worth acting on. On that same test, simple, hand-written rules scored 0.89, and a more advanced machine-learning method ("gradient boosting") scored 0.91–0.93. On the full test of all problem types, rules scored 0.73 and machine learning 0.35.

### What the customer dashboard shows (all 52 practice customers) [D/E]

We built a dashboard that adds up five ways each customer could save money (explained in section 5). The typical (median) saving potential:

| Customer size | Typical saving per year | As a share of their waste cost |
|---|---|---|
| Small (1–3 machines) | **€5.6k** | 22% |
| Medium (4–10 machines) | **€16.4k** | 20% |
| Large (11+ machines) | **€69.4k** | 32% |

Europress doesn't currently tell prospective customers "a customer like you typically saves this much". This table could become that message.

**The demo customer:** a hotel group with 9 machines.

- **Cost:** €140.6k a year, at €283 per tonne. 43% of its waste is recycled.
- **Fill:** its machines are on average only **49% full** when emptied. SMART's target is 85%. So it is paying for many half-empty trips.
- **Savings potential:** **€60.5k a year**, of which €40k comes from emptying only when full.
- **Mixed waste** (the unsorted, most expensive kind) **grew from 56% to 60%** of its tonnes, and its recycling rate fell from 44% to 40% (October–December 2025 compared with July–September 2026).
- **A contract deadline:** it must give notice to its operator by **17 October 2026** if it wants to tender. The data runs to 30 September 2026, so in the data this deadline is 17 days away.

---

## 5. What we sell, and what we deliberately don't

### What we sell

**1. A "ladder" of weight accuracy, built on equipment Europress already has**

The customer climbs only as high as they need:

| Step | How it works | Extra hardware cost | How accurate |
|---|---|---|---|
| **T0: virtual scale** | A software update. The machine estimates weight from data it already collects. | €0 | About ±12–15% for a single pickup, but **±5–6% over a month**, because errors even out [E, our error budget]. In our simulator: 5.3% average error per pickup on machines the model never saw [S] |
| **T1: calibrated with tickets** | Same as T0, but corrected using the operator's weighing tickets when they are available. Adds an alarm if the estimate starts to drift. | €0 | Better than T0 |
| **T2: load cells** | Four load cells under the container's supports, included in the lease. | €3.4–6.3k per machine, installed | In the worst 5% of readings, off by 2.3% [S]. Certified cells (Tier 3): 1.4% [S] |

The plan is to put the T2 scale on just **2–5% of machines**. These act as a trusted reference group (the "golden cohort") used to check and improve the estimates for all the others.

**2. A neutral second opinion**
- Each pickup is compared three ways: **machine weight vs ticket weight vs invoice**. When they disagree, we show the likely reason.
- A comparison of the customer's price per tonne against others, and a scorecard for each operator.
- **Proof of Fullness:** evidence of how full a container really was when it was emptied. This is useful for customers on fixed schedules who suspect they pay for half-empty trips.
- A ready-made report for the legal waste reporting described in section 3 (EU ESRS E5-5 and Poland's BDO).

**3. The customer dashboard (already built)**
- **Every number can be clicked** to show how it was calculated, which data it came from and the exact records behind it.
- It shows **five ways to save**, in euros (explained below).
- An **AI advisor** answers questions about the customer's own data.
- It works in Finnish and English.

**The five ways to save shown on the dashboard:**
1. **Empty when full.** Stop paying for half-empty pickups.
2. **Avoid extra fees.** Wasted trips, cancellations, contamination charges and so on.
3. **Sort more.** Move waste out of the expensive mixed stream into cheaper recyclable streams.
4. **Compare price per tonne.** See whether you pay more than similar customers.
5. **Invoice second look.** Find invoice lines that don't match the contract.

**4. A view for operators (already built)**

This is a trade: operators get useful data, and in return they share their weighing tickets. They get:
- a forecast of which pickups will be needed over the next 14 days,
- how full containers are when they empty them,
- a list of customers whose contracts are coming up for renewal.

### What we do *not* sell or promise

- **Pickup planning or route optimisation.** SMART already does this.
- **Detecting wet or contaminated waste.** The data showed it doesn't work.
- **Official, legally valid weighing for billing.** Not allowed without certified scales.
- **"Gets more accurate with every pickup."** We couldn't prove it.
- **"We recover overcharged money" as the headline.** The data showed little money there.
- **Fully automatic actions.** A person always decides.
- **The name "TrueLoad".** It is already used by a product for overloaded trucks.

### How AI is used

- **Fixed rules make the decisions.** On the full anomaly test, simple rules clearly beat machine learning: a score of 0.73 against 0.35 [D].
- **Claude (an AI model) explains** the findings and **drafts** letters and advice, always pointing to the data behind them.
- **A person approves every action**, either SMART Center staff or the customer.

---

## 6. How it makes money

All prices are **our assumptions** [A]. Europress's real prices should replace them.

| What we offer | Which SMART level it belongs to | Price | Why it's priced this way |
|---|---|---|---|
| **Free weight preview plus a dashboard preview** | SMART Intro. Replaces today's volume calculator. | Free. It costs Europress about €15 per machine per year to provide [E]. | A hook to attract the ~85% of customers who don't use SMART yet. |
| **Verified Weight**, included in SMART Insights | SMART Insights | **The Insights price goes up by €15 per machine per month, or €12 when included in a new lease.** An earlier draft suggested €5–15. | The fee is at most **a third** of what the customer can actually save, so the customer keeps at least two-thirds. Charge chains and fixed-schedule customers. The typical (median) customer stays on the free level. |
| **Proof of Fullness** | Insights. Launch first in Poland and Benelux. | **25% of the verified savings** from avoided pickups in year 1 ("gain-share"), then a normal subscription | Works in markets where "the cheapest offer wins": the customer pays only out of money already saved. |
| **Contract benchmark, action list and reporting pack** | SMART Integrated | +€25 per machine per month, or **€10–40k a year as a licence for a whole chain** | For procurement and sustainability teams at large companies. |
| **Operator Review service** | Integrated / SMART Center | 15% of the money *verifiably* recovered or saved, with a cap | Weight is the evidence that makes the review possible. |
| **Measured tier (real scale platform)** | Lease plus service contract | Europress's current price for its scale platform, inside the lease. It is kept outside the add-on money calculation below. | Only offered where the value is higher than the cost. |
| **Data feed for operators** | Operator API | Free for operators who share tickets. Paid analytics later. | Turns the argument over who owns the data into a fair trade. |
| *An idea from our notes* | SMART | **Discounted SMART for the first 12 months** | The first saving lever (emptying when full) usually pays for it on its own. |

**The price decision: weight is part of SMART Insights, and the Insights price goes up by €15 (€12 in a lease).** We recorded the alternative too:
- A draft plan (`business_sources/message_draft_plan.md`) argued for **€8 per machine per month**. At €8, Europress keeps only about €3.20 per machine per month after costs, so it would need about **3,500 paying machines** just to break even.
- The merged plan picks €12–15. A parallel team working on the same challenge independently arrived at €15.
- **Europress's real SMART prices should replace both.**

---

## 7. Does it pay off?

These are illustrative projections, not forecasts.

| | Pessimistic | Expected | Optimistic |
|---|---|---|---|
| Paying machines in year 3 | ~1,000 | ~3,000 | ~7,000 |
| Yearly recurring revenue from the add-on in year 3 | ~€0.18M | ~€0.6–0.75M | ~€1.8M |
| Share of that revenue left after direct costs (gross margin) | ~75% | ~79% | ~82% |
| When the software pays for itself (break-even) | Never | At about 3,100 machines, early in year 4 | Years 2–3 |

**The finance view: the subscription alone does not pay back.**

To judge an investment, finance teams use **NPV (net present value)**. It adds up all future money in and out, counting money later as worth less than money now (here at 10% a year). A negative NPV means the investment loses value.

- **The subscription on its own** has a 6-year NPV of **+€0.01M**. It roughly breaks even.
- But the add-on should also help Europress **keep service contracts** (we assumed renewals rise by 5 percentage points) and **sell more SMART** (worth about €60 per adopting customer per year). Counting those effects, the expected NPV becomes **+€0.58M** (pessimistic −€0.64M, optimistic +€2.84M), and the investment pays back in year 5 [E]. The real scale platform is sold at Europress's own price, so it is not part of this calculation.

**→ The message for Europress's board:** "Weight makes SMART and the service contract **stickier**", meaning customers stay longer and buy more. It is **not** "a big new revenue line on its own".

For scale: every extra 1 percentage point of customers using SMART is about **120 more machines**, assuming a fleet of about 12,000 machines [A].

---

## 8. The launch plan, with stop signs

Each phase has a clear test. **If the test fails, we stop** rather than keep spending.

| Phase | When | What happens | Go on to the next phase only if… |
|---|---|---|---|
| **0. Pilot** | Q1–Q2 2027 | 10 machines with real scales (the reference group), plus 50 machines with the software-only weight, at 1–2 Finnish chains, with 1 operator sharing tickets. Tamro and Citycon would be natural candidates [F]. | Monthly weight error is 6% or less; at least one operator shares tickets; customers say they'd pay at least €12. |
| **1. Finland launch** | Second half of 2027 | Free weight preview and dashboard for every SMART machine; Verified Weight sold in SMART Insights. | At least 10% of Insights machines take it up, and no operator complains at a senior level. |
| **2. Poland and Benelux** | 2028 | Proof of Fullness on the gain-share model, and cross-checks against Poland's BDO waste register. | At least 30% of pilot sites move from fixed schedules to on-call pickups, and the gain-share earns more than it costs to serve. |
| **3. Platform** | 2029 onwards | The operator data feed at scale, plus anonymous statistics on waste flows. A statistic is only published if it covers at least 5 customers, so nobody can be identified. | Every contract includes consent under the EU Data Act, and a competition-law review is passed. |

- **Cost to start:** about 2–3 full-time people for 6 months (working with Vincit), plus €34–63k for the reference-group scales (10 machines × €3.4–6.3k).
- **Worst case:** because of the stop sign after Phase 0, the most Europress could lose is the Phase 0 budget, about **€211–267k** (itemised in `05_business_plan_addon.md` §6) [E].

---

## 9. Keeping waste operators on side

This is critical. Operators collect the waste, and they are also Europress customers. The product must not look like a weapon against them. It is presented as **"verified service quality for everyone"**:

- **We look for the innocent explanation first.** The data shows most differences have ordinary causes.
- **Findings about an operator's trucks go to that operator first**, before anyone else sees them.
- **Changing operator through a tender is the last resort**, and needs a deliberate decision.
- **We always use neutral language:** "difference" or "needs a second look", never "overcharged" or "fraud".
- **Operators who share their tickets** get a better scorecard and a free data-quality report.
- In the dashboard, the operator table is labelled "neutral, not a verdict", and the AI advisor is instructed to stay neutral.

---

## 10. Risks and how we handle them

| Risk | How we handle it |
|---|---|
| The weight for a single pickup isn't accurate enough | Check at the monthly or contract level, where errors even out. Calibrate with tickets (T1). Add a real scale (T2) where needed. Publish how accurate the numbers are. |
| The typical customer sees no saving (median €0) | Give them the preview and dashboard for free. Charge only chains and fixed-schedule customers. |
| Legal rules on weighing (NAWI) | Always "a second opinion", never "the basis for billing". |
| Operators push back | Neutral explanations, operators hear findings first, and a fair data trade. |
| EU Data Act and competition law | Consent clauses in contracts. Shared statistics include only volumes, never prices, and always cover at least 5 customers. |
| Customers find it too expensive | A free level, pay-from-savings (gain-share) and inclusion in the lease. |
| Our evidence is based on practice data | Every number is labelled. The pilot replaces it with real data. |
| Existing patents | A legal check before committing to any hardware. |
| We don't know how many customers pay for SMART today | Revenue grows in direct proportion to that number. Ask Europress. |

---

## 11. How we would measure success

- **Business:** how many customers use SMART; how many upgrade to Insights or Integrated; how many renew their service contract.
- **Weight quality:** the monthly difference between our weight and a trusted reference; the share of pickups with an operator ticket.
- **Results for customers:**
  - disagreements resolved without escalation;
  - customers moved from fixed schedules to on-call pickups;
  - how full machines are when emptied (aiming for 85%);
  - the share of mixed waste (aiming for it to fall).
- **Efficiency:** what it costs Europress to serve each machine.

---

## 12. Every decision we made, and why

The first seven decisions are about the business. Decisions 8–25 are about the customer dashboard we built.

| # | What we decided | What else we considered | Why | Where the reason came from |
|---|---|---|---|---|
| 1 | Build around **weight**, not around predicting when machines are full | Forecasting fill levels (what other teams did) | Europress said fill prediction already works and "everything is about weight". | Europress briefing |
| 2 | **Improve existing Europress products** (the scale platform, the volume calculator, the SMART levels) instead of creating a new business | A standalone new product | Europress already sells weighing, and its profit is in SMART and service. | Business plan |
| 3 | Present the weight as a **neutral second opinion**, not as the basis for the bill | Official, legally certified weighing | The law (NAWI) doesn't allow it, and the data shows most differences come from the weighbridge side anyway. | Public rules / practice data |
| 4 | **Rules decide, AI drafts, a person approves** | Let machine learning decide; fully automatic actions | Rules performed better in our test, and this keeps trust and good relations with operators. | Practice data |
| 5 | **Free for the typical customer**; charge chains and fixed-schedule customers | Charge everyone | The typical (median) customer gains €0. | Practice data |
| 6 | Include weight in SMART Insights and raise the Insights price by **€15 list, €12 in a lease** | €8 (draft plan), €10, €25 | The fee stays at or below a third of the value, and a parallel team reached the same price. | Section 6 |
| 7 | Tell the board it makes **SMART and service contracts stickier** | "A new revenue line" | On its own, the subscription only breaks even; keeping customers is where the profit is. | Finance view |
| 8 | The main thing we built is a **dashboard for the end customer** that teaches them and shows savings in euros | An internal tool for SMART Center staff | It was our team's goal, and "educate the client" was the top priority in our notes. | Our brief |
| 9 | **Every number can be clicked** to show its formula, sources and records | Plain number tiles | From our brief: "clicking on the value will show where the info is coming from". | Our brief |
| 10 | Show **five separate ways to save** (empty when full, avoid fees, sort more, compare price per tonne, invoice second look) | One headline savings number | Each one can be explained and acted on. | Dashboard |
| 11 | Leave **biowaste and pickups forced by a maximum time limit** out of the "emptied too early" count, and calculate the price-per-tonne saving **after** the "empty when full" saving | Simple raw counts | Biowaste has to be collected often for hygiene, and we must not count the same saving twice. This cut the demo customer's total from 55% to 43% of their cost. | Dashboard |
| 12 | Show our assumptions openly in amber boxes: 85% fill target, 20% of mixed waste could be sorted, 50% of extra fees avoidable, 50% of a price gap could be closed, 1.1 kg of CO₂ per truck km | Hide them | Honesty, and Europress can swap in its own numbers. | Dashboard |
| 13 | Add **"Customers like you"**: typical savings by customer size | — | Europress doesn't advertise typical savings today. | Our notes |
| 14 | Open the demo on a **mid-size customer** (a hotel group with 9 machines), with a switcher for all 52 | The largest chain; a single showcase customer | It tells a story people can relate to: mixed waste rising, a contract deadline coming, half-empty pickups. | Team choice |
| 15 | Add an **operator tab** as a secondary view | Customer view only; a full equal-sized operator product | A side goal: give operators data they don't have. | Team choice |
| 16 | **Finnish by default, with an English switch** | English only | Finland is the home market, with expansion abroad in mind. | Our brief |
| 17 | The AI advisor runs **Claude Code on our own server**, and it can only *read* the data folder | Calling the Anthropic API with custom tools | It matched the brief to demo Claude Code, and needs no separate API key. | Team choice |
| 18 | **Lock the AI down**: it can only read and search files, can't ask for extra permissions, and has limits on usage and spending | — | A security review found a serious weakness: specially crafted text could have changed the AI's settings ("argument injection"). It was fixed. | Security review |
| 19 | The visual design borrows a dashboard layout from Figma (a design tool) and the colours of Europress's SMART website (navy, mint buttons, pink accent) | A pure Figma style; a straight copy of the Europress site | Brief: "match their visual identity with a fresher look". | Our brief |
| 20 | For now the dashboard is reachable **only over a private network** (Tailscale) at http://hackathon.tail8f13e3.ts.net:8080. A public address (europress.acq.ee) comes later. | Public sharing services (Tailscale Funnel, Cloudflare Tunnel) | The current network blocks the standard web ports, and the domain is managed at Zone.ee rather than Cloudflare. The team chose private access. | Team choice |
| 21 | **Building the weight algorithm itself is not part of this track** | — | Another team is building it. | Our brief |
| 22 | **A simpler, cleaner redesign** that follows the design rules of an earlier project ("Haldus"): a fixed set of colours, sizes and corner shapes, with colour used only to show status. It keeps the Europress SMART logo and navy. | Keep the first, more colourful version | Brief: "more minimalistic… clean". The earlier project's colours and logo were explicitly left out. | Our brief |
| 23 | The links on the left open **separate tabs**, not sections of one long page | One long scrolling page | Brief: "links on the left shall show different tabs". | Our brief |
| 24 | Replace the plain customer drop-down with an **account menu and an Account tab** showing contracts and price lists | A simple drop-down | Brief: show "the customer contract and everything there is needing to be known". | Our brief |
| 25 | **Explain the savings straight away**: a "How you save" card right under the headline numbers | One number, with the explanation on a separate tab | Brief: "money saved should explain right away how the money is saved". | Our brief |

---

## 13. Questions we still need Europress to answer

These are things only Europress knows. The answers would replace our assumptions with real numbers.

1. **SMART prices and customers.** What do Intro, Insights and Integrated include today, and what do they cost? How many machines are on paid SMART, and how many customers leave each year?
2. **Machine data for the pilot.** Do the machines keep a record of the pressure on every compaction stroke, and how often is it sampled? Could Europress export data from 10–30 machines, each with at least 20 clean weighing tickets, for a pilot?
3. **The existing scale platform.** What does it cost, how accurate is it, and how much work is it to fit to an existing machine? What is the most extra per month customers would accept?
4. **Data rights.** Can a SMART screen show the customer's invoices and contract details? Who owns that data under the terms of the operator connection and the EU Data Act?
5. **Operators.** Should the operator scorecard be shown to customers, or to operators first? What would persuade operators to share their weighing tickets?
6. **Tolerance.** Would operators accept that a pickup is flagged only when the difference is **both** more than 100 kg **and** more than 10%?
7. **Poland.** How many machines are installed there? Is there a factory (we couldn't find one publicly)? Is the BDO reporting obligation a real pain point for customers?
8. **Service contracts.** What margin do they earn, and how many customers leave? Do leases include SMART?

---

*Where to find more:* the original technical version is `04_business_findings_and_decisions.md`. What Europress told us is in `01_transcript_analysis.md`. How the dashboard works and how every number is calculated is in `02_dashboard.md`. The full source documents are in `business_sources/`.
