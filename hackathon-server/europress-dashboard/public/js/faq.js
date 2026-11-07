// FAQ (facts from the Europress briefing) and method notes, bilingual.
export const FAQ = {
  en: [
    ["How does the machine connect?", "Each machine has a SIM card (4G/5G). Tilt, GPS and movement sensors tell SMART when the container is lifted and transported."],
    ["Does it use a lot of electricity?", "No. The motor is about 3–5 kW and only runs during a compaction cycle — very little compared with the rest of a facility."],
    ["Where does the weight come from?", "From the machine's weight model (fill level, compaction and pressure data), checked against weighbridge tickets when the operator shares them. It is indicative, not legal-for-trade. A platform scale or Scaletipper gives certified-grade weight where needed."],
    ["Why is SMART not a one-off purchase?", "SMART is a service: you pay a service fee and SMART Center optimises your machines every month. There is no up-front fee."],
    ["Who decides about my operator?", "You do. Europress is not part of your contract with the waste operator. SMART gives you neutral data to compare at the next tender (contracts usually run 3 years)."],
    ["Can technicians fix faults remotely?", "Many — SMART Center connects remotely, sees sensor and electrical states and can solve e.g. blown fuses without a visit."],
    ["What does E-stop mean?", "Emergency stop."],
  ],
  fi: [
    ["Miten laite on yhteydessä verkkoon?", "Jokaisessa laitteessa on SIM-kortti (4G/5G). Kallistus-, GPS- ja liikeanturit kertovat SMARTille, milloin kontti nostetaan ja kuljetetaan."],
    ["Kuluttaako laite paljon sähköä?", "Ei. Moottori on noin 3–5 kW ja käy vain puristusjakson aikana — hyvin vähän verrattuna kiinteistön muuhun kulutukseen."],
    ["Mistä painotieto tulee?", "Laitteen painomallista (täyttöaste, puristus- ja painetiedot), ja se tarkistetaan punnituslippuja vasten, kun operaattori jakaa ne. Tieto on suuntaa-antava, ei kaupalliseen punnitukseen hyväksytty. Lavavaaka tai Scaletipper antaa tarkan painon, kun sitä tarvitaan."],
    ["Miksi SMART ei ole kertaostos?", "SMART on palvelu: maksat palvelumaksua ja SMART Center optimoi laitteitasi kuukausittain. Aloitusmaksua ei ole."],
    ["Kuka päättää operaattoristani?", "Sinä. Europress ei ole osapuoli sopimuksessasi jätehuoltoyhtiön kanssa. SMART antaa neutraalia dataa vertailuun seuraavassa kilpailutuksessa (sopimukset ovat yleensä 3-vuotisia)."],
    ["Voiko vikoja korjata etänä?", "Monia — SMART Center ottaa etäyhteyden, näkee anturien ja sähköjen tilan ja voi ratkaista esim. palaneet sulakkeet ilman käyntiä."],
    ["Mitä E-stop tarkoittaa?", "Hätäpysäytys."],
  ],
};

export const METHOD = {
  en: [
    ["Data", "Synthetic Europress competition pack: 52 customers, 447 machines, 12 months (Oct 2025 – Sep 2026), contracts, telemetry, and billing + weighbridge data shared by the waste-operator partners (customers never upload invoices). All prices are hypothetical."],
    ["Savings levers", "Five levers, each clickable: (1) empty at 85 % fill instead of earlier — biowaste and max-interval pickups excluded; (2) 50 % of penalty and extra fees avoided; (3) 20 % of mixed waste moved to recyclable streams; (4) close half the gap to the fleet-median €/t at the next tender; (5) invoice lines that differ from your contract price list."],
    ["Recycling rate", "Tonnes of cardboard, paper, plastics and biowaste ÷ all tonnes. Mixed waste is the only non-recycled stream in the data."],
    ["CO₂", "Truck trips × billable round-trip km × 1.1 kg CO₂/km (diesel refuse truck, assumption)."],
    ["Operator scorecard", "On-time rate, missed visits, share of weighbridge tickets shared within 7 days, and order-to-pickup lead time. Neutral information to support a conversation, never a verdict."],
    ["AI advisor", "Claude (Anthropic) runs on the Europress server with read-only access to the same data files; it cannot browse the web or change anything. It always names the file it used."],
  ],
  fi: [
    ["Data", "Synteettinen Europress-kilpailuaineisto: 52 asiakasta, 447 laitetta, 12 kk (loka 2025 – syys 2026), sopimukset, telemetria sekä jäteoperaattorikumppanien jakamat laskutus- ja punnitustiedot (asiakkaat eivät koskaan lähetä laskuja). Kaikki hinnat ovat kuvitteellisia."],
    ["Säästövivut", "Viisi vipua, jokainen avattavissa: (1) tyhjennys 85 % täyttöasteella aiemman sijaan — biojäte ja enimmäisvälin tyhjennykset pois lukien; (2) 50 % sanktioista ja lisämaksuista vältetään; (3) 20 % sekajätteestä siirtyy kierrätysjakeisiin; (4) puolet erosta laitekannan mediaani-€/t:hen suljetaan kilpailutuksessa; (5) laskurivit, jotka poikkeavat sopimushinnastosta."],
    ["Kierrätysaste", "Kartongin, paperin, muovien ja biojätteen tonnit ÷ kaikki tonnit. Sekajäte on aineiston ainoa kierrättämätön jae."],
    ["CO₂", "Kuorma-autokäynnit × laskutettava edestakainen matka × 1,1 kg CO₂/km (dieselkäyttöinen jäteauto, oletus)."],
    ["Operaattorin tuloskortti", "Ajallaan-osuus, väliin jääneet käynnit, 7 päivän sisällä jaettujen punnituslappujen osuus ja tilauksesta tyhjennykseen kulunut aika. Neutraalia tietoa keskustelun tueksi, ei tuomio."],
    ["Tekoälyneuvoja", "Claude (Anthropic) toimii Europressin palvelimella ja sillä on vain lukuoikeus samoihin datatiedostoihin; se ei voi selata verkkoa eikä muuttaa mitään. Se kertoo aina, mitä tiedostoa käytti."],
  ],
};
