# Every problem, its solution, and why that solution

**Europress × Since AI 2026**, 7 November 2026. Companion to the plan at https://claude.ai/artifact/MeVR2iDqkQvdfK25AYEpMp and to `05_business_plan_addon.md`.

This file is for someone who has read nothing else. Each chapter takes one problem Europress told us about, in plain words: what the problem is, what we propose to do about it, and why that is the right fix rather than something else. Every chapter ends with the test that would show the fix worked.

**Three things to know before you start**

- **Europress** makes compactors: machines that press waste into a container at a shop, hotel, hospital or factory. Its connected service, **SMART**, knows how *full* each machine is and orders the truck. About 15 % of customers use SMART.
- **The waste operator** is a different company. It sends the truck, weighs the load at its own plant, and bills the customer by the tonne. The operator is the only one who knows the weight. Operators are also Europress customers, because they lease machines too.
- **The numbers in the examples come from a practice dataset** that Europress invented for the competition: 52 made-up customers, 5 made-up operators, invented prices. The example customer, "Hospitality Customer 0049", is a hotel group with 3 sites and 9 machines. The numbers show what the product *would* show; none of them is a real Europress figure.

---

## Problem 1 · Nobody on the customer's side knows the weight

**The problem.** Every invoice and every contract in waste is priced per tonne. The only party that weighs the waste is the operator, who is also the party being paid per tonne. Europress's own words: "We only estimate. We have no evidence." The machine knows it is 79 % full, but nobody knows whether that is 1.2 tonnes or 1.6 tonnes, and the customer pays for the difference.

For the hotel group, 395 pickups happened in a year. Only 37 of them, 9 %, came with a weighing ticket the customer could look at. The other 358 are a number on an invoice and nothing else.

**The solution.** Make the machine itself estimate the weight, and give every pickup a weight with a range, such as "1,400 kg, most likely between 1,240 and 1,560 kg".

The estimate is a **soft sensor**: a piece of software, not a scale. It uses data the compactor already sends every hour: how full it is, how many times the ram has pressed, how much hydraulic pressure the ram needed, how warm the oil is, plus the last week's rain and humidity from the Finnish Meteorological Institute. Wet or dense waste needs more pressure at the same fill, and that is what separates a heavy load from a light one.

The software is taught on real weights from two places: a small group of machines that get real scales fitted underneath (four load cells, about €3,400–6,300 per machine, on 2–5 % of the fleet), and the weighing tickets that some operators already share. Each machine is then corrected by its own tickets, and an alarm fires if its estimate starts to drift away from them.

With this, the hotel group could check 96 % of its pickups instead of 9 %.

**Why this solution.**

- *Why not a scale on every machine?* A scale platform costs about as much as the compactor. Europress has sold them for years and "few want it". Software costs nothing per machine.
- *Why not software alone?* An estimate with nothing real to check it against drifts and cannot be trusted in a dispute. The few real scales and the shared tickets are the anchor. This is the hybrid Tommi, the Europress representative, suggested himself: "a very cheap sensor somewhere as a reference point, and then this trained model".
- *Why pressure and weather?* Fill level alone cannot tell a light load from a heavy one. The dashboard's current fill-only estimate has a median error of 7 %. In our simulator, adding pressure, strokes and weather brought the error on unseen machines to about 4.7 %. Europress also said it has "no long-term data on how density varies, for example cardboard in winter versus summer", so weather is new information for them too.
- *Why a range and not one number?* Because the number is an estimate, and saying so is what makes it credible to an operator. The range is set so that the true weight falls inside it about 80 % of the time.
- *Why we are not sure yet.* Our two studies disagree. The simulator says 4.7 %. A separate hardware study, modelling cases where water and stiffness change the mass without changing the pressure, says pressure alone can be off by 29 % in the worst 5 % of cases. So the plan's first step is a €0 test: run archived pressure data from 10–30 machines against their tickets and see who is right, before buying anything.

**How we know it worked.** Monthly weight error against the machines with real scales is 6 % or less, and the share of pickups the customer can check rises from 9 % to over 90 %.

---

## Problem 2 · The customer cannot answer "am I paying the right amount?"

**The problem.** Europress listed the questions its customers cannot answer today: Am I paying the right amount? Is the operator doing its best? Are the service levels in the contract being kept? Would another operator serve me better? The customer has an invoice, a contract and a truck that comes and goes, and no way to connect them.

For the hotel group: the operator, "Hauler Delta", arrives on time for 57 % of pickups, shares none of its weighing tickets, takes a median 37 hours from order to truck, and made 6 wasted trips. The contract can be put out to tender, and notice is due by 17 October. None of this is visible to the customer today.

**The solution.** A **contract and service card** on the customer's home page, fed by the weight from Problem 1 and by the records SMART already has (when the truck was ordered, when it came, how full the machine was). It says, in one sentence: "Hauler Delta arrives on time for 57 % of pickups and shares no weighing tickets. Your contract can be tendered. Give notice by 17 October 2026." A click shows the numbers behind it, and a second operator's figures next to them for comparison.

Each pickup is also reconciled: machine weight against ticket against invoice line. When they agree, the pickup is marked "checked". When they disagree repeatedly, the customer sees "needs a second look".

**Why this solution.**

- *Why a scorecard and not an accusation?* Europress is "not a party" to the customer's contract with the operator. Its role, in its own words, is to be a "safeguard on behalf of the customer". A neutral card with facts does that. The words "overcharged" and "fraud" never appear, because they are legal claims an estimate cannot prove, and because the operator is also a Europress customer.
- *Why does the operator see it first?* Every finding about an operator goes to that operator five working days before the customer sees it, so they can explain. In the practice data, most gaps between machine and ticket had ordinary causes, such as a stored container weight that was over a year old. A protocol that assumes an honest mistake first keeps operators sharing tickets.
- *Why "tender" and "notice date"?* Contracts usually run 3 years and then go to tender, and Europress told us "the customer chooses the next operator" but "lacks tools to compare". The notice date is the one moment the customer has leverage, and most customers miss it.
- *Why not ask the customer to upload invoices?* We asked. Tommi's answer was that point-to-point links with thousands of customers are "probably not feasible". Instead the plan integrates with the roughly 20 operators in Finland, who have the data.

**How we know it worked.** Disagreements between customers and operators are settled from the dashboard without escalation, and the share of pickups marked "checked" rises every quarter.

---

## Problem 3 · Customers are not experts, and most information is ignored

**The problem.** Tommi was blunt about it: "It gives a lot of information, but I think 60 or 70 % is ignored." Customers do not have a waste expert on staff. They will not read a report. He asked for "instructions for dummies", and "how would you tell it to your grandmother", and summed it up as "simplify, simplify, simplify".

**The solution.** The customer's home page becomes **five answers**, not a dashboard. Five cards, in Tommi's own order: cost, safety, CO₂, contract, recycling. Each card is one sentence a non-expert understands, with a colour: green, amber or red. For the hotel group the cost card reads: "You pay €140,574 a year. About €60,000 of it can be saved." The second line says where: "Most of it goes on trucks emptying half-full machines (49 % full on average)."

Clicking a card opens the next level: why, and the numbered steps to take. Clicking again shows the formula and the rows of data it came from. When a card turns red, the customer gets an email. Once a month, the customer gets a four-sentence email instead of a report.

**Why this solution.**

- *Why answers and not charts?* Because a chart asks the reader to work out what it means, and 60–70 % of readers do not. A sentence with a colour can be acted on by anyone, including the hotel manager who has never thought about waste.
- *Why these five topics?* They are Tommi's framework, word for word, from the second briefing. We added nothing and merged nothing.
- *Why cost first?* It is the card that answers "why should I care", and it is the card that leads to a sale. Reducing one pickup, Europress said, "pays for itself".
- *Why keep the details at all?* Because trust needs them. Every number in the dashboard opens to show its formula and the data rows behind it. The expert at a chain's procurement department wants that; the hotel manager never clicks it. Both are served.
- *Why email?* Tommi described it himself: "a flag to the office that says you should go to the customer". People do not open dashboards; they open email.

**How we know it worked.** Weekly active users go up, and the share of visits where at least one card is opened to its explanation is tracked.

---

## Problem 4 · Salespeople do not know what to tell the customer

**The problem.** Europress sells SMART to only about 15 % of its customers. Its salespeople see a lot of data and, in Tommi's words, "need very clear answers: tell me what I should tell to the customer". Talking to a human takes time, so the time has to be spent on the right customer with the right sentence.

**The solution.** **Sales briefs.** Every night, fixed rules rank all customers by what is at stake: a contract whose notice date is near, trucks emptying half-full machines, mixed waste rising, machines standing full for hours. For the customers at the top, Claude writes three sentences, each citing the data behind it. For the hotel group: "You could save about €60k a year. Most of it comes from trucks emptying your machines when they are only half full. SMART on-call fixes that." A salesperson reads it, edits if needed, presses Approve, and it becomes a task in the CRM with the offer attached.

**Why this solution.**

- *Why rules rank and not the AI?* A rule can be explained to a salesperson in one line ("notice date within 90 days"). On our benchmark, fixed rules also beat a machine-learning classifier at spotting the right cases (macro-F1 0.73 against 0.35). Rules are auditable; a model's ranking is not.
- *Why Claude writes?* Turning numbers into three plain sentences is what a language model is good at. Every sentence must cite the row it came from, and a check rejects any sentence whose citation does not resolve, so it cannot invent a figure.
- *Why a person approves?* The worst thing in the plan's risk list is Claude telling a customer something wrong. Approval costs a salesperson thirty seconds and removes that risk.
- *Why free?* Each percentage point of SMART adoption is about 120 more machines, worth roughly €21,600 a year in subscriptions plus service contracts that renew more often. A brief costs cents. Charging for it would be pointless.

**How we know it worked.** Five salespeople use the briefs every week, briefs lead to booked meetings, and SMART adoption climbs past 15 %.

---

## Problem 5 · Europress has nothing to offer the operators

**The problem.** "We should be able to offer something to operators too; today we can't." Operators are the party with the trucks, the weighbridges and the tickets. They are also Europress customers. Anything that looks like a tool against them loses twice: the relationship and the data.

**The solution.** An **operator feed**: the next 14 days of predicted pickups across all the operator's Europress machines, with the expected tonnes of each one, how full the machine will be, and which of its customer contracts are coming up for renewal. It arrives inside the operator's own planning system (AMCS, WasteHero, Ecomond) as a data feed, not as yet another website. It is free, on one condition: the operator shares its weighing tickets back.

**Why this solution.**

- *Why tonnes?* Bramidan, a competitor, already sends pickup schedules to haulers. Tonnes are what no fill sensor can give. A hauler who knows the expected weight can fill its trucks and plan its weighbridge.
- *Why free for tickets?* Europress told us it does not sell data: "the customer owns their own data". A trade avoids that fight. And the tickets are exactly what the weight estimate in Problem 1 needs to stay calibrated. Both sides give something they already have and get something they lack.
- *Why inside their system and not a portal?* Tommi: "We don't need to reinvent the wheel, but there are ways to connect those together." Operators plan in their ERP all day; they will not log into a Europress page.
- *Why this makes the whole plan safer.* The communication plan (Problem 2) depends on operators cooperating. An operator that gets a useful free feed every day is an operator that answers a "please re-weigh this tare" note.

**How we know it worked.** At least one operator's system receives the feed daily and shares 90 % or more of its tickets back.

---

## Problem 6 · Nobody knows what winter, frost and rain do to the waste

**The problem.** Europress: "We have no long-term data on how volume and density vary, for example cardboard in winter versus summer." Biowaste freezes to the container walls and empties only partly. Rain gets into open-hopper cardboard and the customer pays for water by the tonne. Snow on the roof adds false weight.

**The solution.** Bring **weather into the system** in two ways. First, as an input to the weight estimate: the last seven days of rain and humidity at each site. Second, as a trigger for concrete alerts. "A rainy week is coming in Salo. Close the hopper lids on cardboard machines." "Frost below −15 °C for three days at Raahe. Collect the biowaste before the cold spell." The weather comes from the Finnish Meteorological Institute's open data. A fleet map shows the machines, their fill at emptying, their tonnes, and the weather, so a chain or an operator sees the whole picture at once.

**Why this solution.**

- *Why free weather data?* FMI's open data is licensed for commercial use at no cost. A paid weather service would add nothing for Finland. (This page's mockups use another free source, Open-Meteo, whose terms do not allow commercial use, so it is for the mockups only.)
- *Why alerts rather than a weather page?* Because nobody reads a weather page. An alert names a site, a cause and an action. In the simulator, wet open-hopper cardboard weighed 4–6 % more; one closed lid is money.
- *Why honest about how much it helps?* Over a whole year, weather changes the average weight error very little. It matters on the specific wet and frozen days when a bill is wrong, and those are the days a customer notices.
- *Why a map?* A list of 34 municipalities says less than their positions. Lapland's remote-pickup surcharges and the northern frost both live on a map, and it shows at a glance where trucks drive half-empty, which is where the sales case is.

**How we know it worked.** In the first real test, weather features lower the weight error on wet and frozen days, and alerts are acted on (a lid closed, a pickup moved).

---

## Problem 7 · Waste quality is not measured, and mixed waste is growing

**The problem.** Mixed waste is the most expensive stream and the one that cannot be recycled. For the hotel group it rose from 55 % to 58.5 % of all tonnes in a year, while the recycling rate fell from 44 % to 40 %. Contaminated loads of cardboard or plastic are rejected at the plant, burned, and charged a fee. Tommi called quality "our next exercise" and said that with weight and quality together Europress would be "in a super position".

**The solution.** In two stages. **Stage 1**, now: use the quality grades the operators' plants already record. The practice data holds 6,721 of them. Show them per machine: how many loads were accepted, how many rejected, and where the contamination is. The advisor explains what to sort better: for the hotel group, moving 20 % of mixed waste into cardboard saves about €6,300 a year. **Stage 2**, in 2028: a camera in the hopper of mixed-waste and plastic machines, with a licensed recognition model, scoring each load before it leaves.

**Why this solution.**

- *Why grades first?* They already exist and cost nothing. Showing them needs a week of work and no hardware.
- *Why accepted versus rejected, not A to D?* Tommi told us plants do not grade finely: "either it's total crap or it's fine". So the dashboard shows accepted or rejected, which is what happens.
- *Why cameras only on mixed waste and plastic?* Those are the streams with rejection fees. On a cardboard machine a camera would cost more than the fees it prevents.
- *Why not build the camera model ourselves?* Companies such as WasteVision and Greyparrot already sell one. Europress should buy the model and own the data.
- *Why weight and quality together matter.* Weight times grade is the material value of a pickup. That is the number a recycling market pays for, and nobody can produce it today.

**How we know it worked.** The share of mixed waste falls, and rejected loads fall, at the pilot sites.

---

## Problem 8 · Customers need numbers for environmental reporting

**The problem.** Chains and property companies have to report their waste: tonnes per stream, recycling rate, transport emissions. Today they get those figures from the operator's portal, if the operator has one, in the operator's format. Europress mentioned "environmental reporting" as something an AI could help with, and Polish customers must file with a national waste register called BDO.

**The solution.** A **reporting pack**: one click produces a quarter's figures per site and for the whole chain, in the three formats people actually file: the EU sustainability standard for resource use (ESRS E5), the greenhouse-gas protocol's category for waste (Scope 3, category 5), and the Polish BDO register. Every cell in the export can be traced back to the pickups behind it.

**Why this solution.**

- *Why these three formats?* They are the ones a sustainability team is asked for. Everything else is a subset.
- *Why traceable?* An auditor's first question is "where does this number come from". The dashboard already stores every number with its formula and rows, so the export inherits that for free.
- *Why we call it voluntary.* The EU narrowed mandatory sustainability reporting in 2026 to companies with over 1,000 staff and €450M turnover. Most Europress customers are below that. They report because their own customers and lenders ask, so the pack is sold on usefulness, not compliance.
- *Why Europress must have it anyway.* Operator portals such as Stena's and L&T's already offer CO₂ and sustainability exports. Without one, Europress's dashboard would be the only place a customer cannot get them.

**How we know it worked.** Reports are exported every quarter by the chains that have the pack.

---

## Three problems the plan creates for itself, and how it handles them

**The median customer saves nothing.** In the practice data, half the customers have no savings to find. Charging them would fail. So the five answers are free for everyone, as the hook for the 85 % of customers not on SMART, and only chains and fixed-schedule customers, where the savings are real, pay €15 per machine per month for the verified weight. The fee is kept under a third of what they save.

**The weight could be wrong.** Our two studies disagree, as Problem 1 explains. So the roadmap runs a €0 test on archived data first, fits real scales to a reference group before trusting the estimate, publishes the monthly accuracy openly, and stops at a gate if the numbers are not met. The most Europress can lose is the first phase's budget, about €270k.

**The add-on alone does not pay back.** The subscriptions, on their own, have a negative value over six years (−€0.33M). We say so, rather than dress it up as a new revenue line, because the real value is elsewhere: customers who can see their weight buy SMART and renew their service contracts, which is where Europress makes its profit. Counted that way, the value turns positive (+€0.23M in the expected case).

---

## The one idea behind all eight

Every problem above comes from the same gap: the machine knows how full it is, nobody on the customer's side knows how heavy the waste is, and everything is priced by weight. Fill that gap once, with software on machines Europress already owns, and each of the eight problems becomes a short rule plus a plain sentence. That is the plan.
