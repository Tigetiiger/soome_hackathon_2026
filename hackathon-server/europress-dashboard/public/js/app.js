// Europress SMART Insights — app controller: tab routing, account switcher, language, customer views.
import { t, setLang, getLang, applyStatic, fmt, eur, stream, sector, date, month } from "./i18n.js";
import { costChart, recyclingChart, weightChart, densityChart, gaugeSvg, STREAM_COLORS } from "./charts.js";
import { openTrace, openInfo, deviceTrace, closePanels, setAskHandler, esc } from "./drawer.js";
import { renderEpOverview, renderEpPipeline, renderEpFleet, renderEpData, renderSalesAlerts } from "./europress.js";
import { initAi, openAi, setAskContext } from "./ask.js";
import { renderOperator } from "./operator.js";
import { renderAccount, initials } from "./account.js";
import { FAQ, METHOD } from "./faq.js";
import { renderMachinesNow } from "./machines.js";
import { renderTrends } from "./trends.js";
import { renderAnswers } from "./answers.js";
import { renderWeightModel } from "./weightmodel.js";

const el = (id) => document.getElementById(id);
const VIEWS = ["overview", "savings", "machines", "contracts", "weight", "trends", "account", "operators", "faq",
  "ep-overview", "ep-pipeline", "ep-fleet", "ep-data"];
const WS_HOME = { customer: "#overview", europress: "#ep-overview", partners: "#operators" };
const NAV_KEY = { overview: "title.overview", savings: "nav.savings", machines: "nav.machines", contracts: "nav.operators",
  weight: "nav.weight", trends: "nav.trends", advisor: "nav.advisor", account: "account.details", operators: "title.operator", faq: "title.faq",
  "ep-overview": "title.ep.overview", "ep-pipeline": "title.ep.pipeline", "ep-fleet": "title.ep.fleet", "ep-data": "title.ep.data" };
const STATUS_STATE = { good: "good", review: "warn", action: "bad" };
const EFFORT_STATE = { low: "good", medium: "warn", high: "info" };
const SEARCH_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4-4"/></svg>';
const state = { mv: { overview: "design", machines: "mixed" }, index: null, customer: null, route: "overview", ws: "customer", cache: new Map() };

function wsOf(view) {
  if (view.startsWith("ep-")) return "europress";
  if (view === "operators") return "partners";
  if (view === "advisor" || view === "faq") return state.ws;
  return "customer";
}

async function getJson(url) {
  if (state.cache.has(url)) return state.cache.get(url);
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  const data = await res.json();
  state.cache.set(url, data);
  return data;
}

function bindRows(tbl, fn) {
  tbl.querySelectorAll("tr.click").forEach((tr) => {
    const go = () => fn(Number(tr.dataset.i));
    tr.addEventListener("click", go);
    tr.addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
  });
}

// ---------------------------------------------------------------- overview
const KPI_ICON = { savings: "target", total_cost: "pie-chart", eur_per_t: "down", recycling_rate: "up" };
function kpiCard({ key, value, unit, sub, primary }) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = `kpi${primary ? " primary" : ""}`;
  b.innerHTML = `<img class="kpi-icon42" src="/img/icons/${KPI_ICON[key]}.svg" width="42" height="42" alt="">
    <div class="kpi-label"><span>${esc(t(`kpi.${key}`))}</span>${SEARCH_ICON}</div>
    <div class="kpi-value">${value}${unit ? `<small>${unit}</small>` : ""}</div><div class="kpi-sub">${esc(sub)}</div>`;
  b.addEventListener("click", () => (key === "savings" ? location.hash = "#savings"
    : openTrace(state.customer.kpis[key], t(`kpi.${key}`), `kpis.${key}`)));
  return b;
}

function renderKpis(p) {
  const k = p.kpis;
  el("kpis").replaceChildren(
    kpiCard({ key: "total_cost", value: eur(k.total_cost.value), sub: t("kpi.sub.total_cost", { lifts: fmt(k.lifts.value), t: fmt(k.tonnes.value) }) }),
    kpiCard({ key: "eur_per_t", value: fmt(k.eur_per_t.value), unit: "€/t", sub: t("kpi.sub.eur_per_t") }),
    kpiCard({ key: "recycling_rate", value: fmt(k.recycling_rate.value, 1), unit: "%", sub: t("kpi.sub.recycling_rate") }),
  );
}

function renderHero(p) {
  const k = p.kpis;
  el("heroValue").textContent = eur(k.savings.value);
  el("heroDelta").textContent = `↓ ${Math.round((k.savings.value / k.total_cost.value) * 100)} % ${t("hero.ofCost")}`;
}

function renderProblems(p) {
  const c = p.compare;
  el("probPeriod").textContent = `${month(c.last_months[0])}–${month(c.last_months[1])} vs ${month(c.prev_months[0])}–${month(c.prev_months[1])}`;
  const val = (v, unit) => (v == null ? "" : unit === "date" ? date(v) : unit === "€" ? eur(v) : `${fmt(v, unit === "%" ? 1 : 0)} ${unit}`);
  const list = p.problems.length ? p.problems : [{ id: "none", unit: "" }];
  el("problems").innerHTML = list.map((x, i) => x.id === "none" ? `<li><span class="what"><b>${esc(t("prob.none"))}</b></span></li>` : `<li>
      <span class="what"><b>${esc(t(`prob.${x.id}`, { operator: x.operator || "" }))}</b>
        <span class="chg">${x.from != null ? `${esc(val(x.from, x.unit))} → ` : ""}<strong>${esc(val(x.to, x.unit))}</strong></span>
        <span class="act">${esc(t(`act.${x.action}`))}</span></span>
      ${x.eur ? `<span class="eur">${eur(x.eur)}</span>` : "<span></span>"}
      <button type="button" class="ask-link" data-p="${i}">${esc(t("ai.cta"))} →</button></li>`).join("");
  el("problems").querySelectorAll("button[data-p]").forEach((b) => {
    const x = list[Number(b.dataset.p)];
    b.addEventListener("click", () => openAi(`${t(`prob.${x.id}`, { operator: x.operator || "" })}: ${x.from != null ? val(x.from, x.unit) + " → " : ""}${val(x.to, x.unit)}. ${t("prob.askWhy")}`, `problems.${x.id}`));
  });
}

function renderHowSave(p) {
  const total = p.kpis.savings.value || 1;
  el("saveTitle").textContent = t("save.title", { eur: eur(p.kpis.savings.value) });
  if (el("saveBar")) el("saveBar").innerHTML = p.levers.map((l) => `<i style="width:${((l.saving_eur || 0) / total) * 100}%"></i>`).join("");
  el("howSave").innerHTML = p.levers.map((l, i) => `<li data-i="${i}" tabindex="0" role="button">
      <b class="ttl"><span class="lead-in" data-effort="${l.effort}">${esc(t(`effort.${l.effort}`))}: </span>${esc(t(`lever.${l.id}`))}</b>
      <span class="eur">${eur(l.saving_eur)}</span>
      <span class="n">${String(i + 1).padStart(3, "0")}</span>
      <span class="desc">${esc(t(`lever.${l.id}.d`))}</span></li>`).join("");
  el("howSave").querySelectorAll("li").forEach((li) => {
    const l = p.levers[Number(li.dataset.i)];
    const go = () => openTrace(l.trace, t(`lever.${l.id}`), `levers.${l.id}`, t(`lever.${l.id}.d`));
    li.addEventListener("click", go);
    li.addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
  });
}

function renderInsights(p) {
  const list = p.insights.length ? p.insights : [{ id: "mixed_falling", params: { from: "–", to: "–" }, severity: "good" }];
  el("insights").innerHTML = list.map((ins, i) => {
    const params = Object.fromEntries(Object.entries(ins.params).map(([k, v]) =>
      [k, typeof v === "number" ? fmt(v, Number.isInteger(v) ? 0 : 1) : k === "date" ? date(v) : v]));
    return `<li><span class="state" data-state="${ins.severity}">${esc(t(`sev.${ins.severity}`))}</span>
      <div>${esc(t(`ins.${ins.id}`, params))}<br><button type="button" data-ins="${i}">${esc(t("ai.cta"))} →</button></div></li>`;
  }).join("");
  el("insights").querySelectorAll("button[data-ins]").forEach((b) => {
    const ins = list[Number(b.dataset.ins)];
    b.addEventListener("click", () => openAi(t(`ins.${ins.id}`, ins.params), `insights.${ins.id}`));
  });
}

function costStreamTrace(p, s) {
  const cost = p.monthly.cost_by_stream[s] || [];
  const tons = p.monthly.tonnes_by_stream[s] || [];
  const sumC = cost.reduce((a, b) => a + (b || 0), 0), sumT = tons.reduce((a, b) => a + (b || 0), 0);
  return {
    value: sumC, unit: "EUR",
    formula: { en: `Σ invoice lines for ${stream(s)} machines per billing month. ${fmt(sumT, 1)} t → ${fmt(sumT ? sumC / sumT : null)} €/t.`,
               fi: `Σ laskurivit ${stream(s).toLowerCase()}-laitteille laskutuskuukausittain. ${fmt(sumT, 1)} t → ${fmt(sumT ? sumC / sumT : null)} €/t.` },
    sources: ["finance/invoices.parquet", "finance/invoice_lines.parquet", "reference/devices.parquet"],
    rows: { columns: ["month", "cost_eur", "tonnes"], rows: p.period.months.map((m, i) => [m, cost[i], tons[i]]), total_rows: p.period.months.length },
  };
}

// ---------------------------------------------------------------- savings, machines, contracts, weight
function renderSavings(p) {
  const tbl = el("leversTable");
  tbl.innerHTML = `<thead><tr><th>${t("col.lever")}</th><th>${t("col.effort")}</th><th class="num">${t("col.saving")}</th></tr></thead><tbody>${
    p.levers.map((l, i) => `<tr class="click" data-i="${i}" tabindex="0">
      <td><span class="strong">${esc(t(`lever.${l.id}`))}</span><span class="desc">${esc(t(`lever.${l.id}.d`))}</span></td>
      <td><span class="state" data-state="${EFFORT_STATE[l.effort]}">${esc(t(`effort.${l.effort}`))}</span></td>
      <td class="num strong">${eur(l.saving_eur)}</td></tr>`).join("")}
    <tr><td class="strong">${t("total")}</td><td></td><td class="num strong">${eur(p.kpis.savings.value)}</td></tr></tbody>`;
  bindRows(tbl, (i) => openTrace(p.levers[i].trace, t(`lever.${p.levers[i].id}`), `levers.${p.levers[i].id}`, t(`lever.${p.levers[i].id}.d`)));

  const target = state.index.assumptions.target_fill_pct;
  const v = p.kpis.avg_fill.value;
  el("gaugeSub").textContent = t("card.gauge.sub", { target });
  el("gauge").innerHTML = `${gaugeSvg(v, target)}<div class="gauge-center"><b>${fmt(v)} %</b><span>${t("gauge.label")}</span></div>`;
  el("gaugeStats").innerHTML = [[fmt(p.kpis.lifts.value), t("gauge.lifts")], [fmt(p.early_lifts_n), t("gauge.early")],
    [fmt(p.wasted_trips_n), t("gauge.wasted")], [`${target} %`, t("gauge.target")]]
    .map(([val, lab]) => `<div><dt>${esc(lab)}</dt><dd>${val}</dd></div>`).join("");

  const n = p.customer.n_devices;
  const seg = n <= 3 ? "small" : n <= 10 ? "medium" : "large";
  const s = state.index.segments[seg];
  el("peersText").innerHTML = `<b>${s.saving_pct} %</b><span>${esc(t("peers.short", { seg: t(`seg.${seg}`), eur: eur(s.median_saving) }))}</span>`;
}

function renderMachines(p) {
  const tbl = el("devicesTable");
  tbl.innerHTML = `<thead><tr><th>${t("col.machine")}</th><th>${t("col.stream")}</th><th>${t("col.fill")}</th>
    <th class="num">${t("col.eurt")}</th><th class="num">${t("col.peer")}</th><th>${t("col.status")}</th></tr></thead><tbody>${
    p.devices.map((d, i) => {
      const fill = d.avg_fill_pct ?? 0;
      const fs = fill >= 75 ? "good" : fill >= 55 ? "warn" : "bad";
      return `<tr class="click" data-i="${i}" tabindex="0">
        <td class="strong">${esc(d.device_id)}<span class="desc">${esc(d.site)} · ${fmt(d.volume_m3)} m³</span></td>
        <td><span class="dot" style="background:${STREAM_COLORS[d.stream]}"></span>${esc(stream(d.stream))}</td>
        <td><span class="fill"><span class="fill-bar" data-state="${fs}"><i style="width:${fill}%"></i></span>${fmt(fill)} %</span></td>
        <td class="num">${fmt(d.eur_per_t)}</td><td class="num">${fmt(d.peer_median_eur_per_t)}</td>
        <td><span class="state" data-state="${STATUS_STATE[d.status]}">${esc(t(`status.${d.status}`))}</span></td></tr>`;
    }).join("")}</tbody>`;
  bindRows(tbl, (i) => openTrace(deviceTrace(p.devices[i]), `${p.devices[i].device_id} · ${stream(p.devices[i].stream)}`, `devices.${p.devices[i].device_id}`));
}

function renderContracts(p) {
  const soon = new Date("2027-04-01");
  const tbl = el("operatorsTable");
  tbl.innerHTML = `<thead><tr><th>${t("col.operator")}</th><th class="num">${t("col.ontime")}</th><th class="num">${t("col.shared")}</th>
    <th class="num">${t("col.leadtime")}</th><th>${t("col.notice")}</th></tr></thead><tbody>${
    p.operators.map((o, i) => `<tr class="click" data-i="${i}" tabindex="0">
      <td class="strong">${esc(o.name.replace(" (fictional)", ""))}<span class="desc">${o.contracts} ${t("col.contracts").toLowerCase()}</span></td>
      <td class="num">${fmt(o.on_time_rate)} %</td><td class="num">${fmt(o.weighbridge_shared_rate)} %</td><td class="num">${fmt(o.order_to_lift_h)} h</td>
      <td><span class="state" data-state="${new Date(o.notice_by) < soon ? "bad" : "mute"}">${esc(date(o.notice_by))}</span></td></tr>`).join("")}</tbody>`;
  bindRows(tbl, (i) => openTrace(p.operators[i].trace, p.operators[i].name, `operators.${p.operators[i].operator_id}`));
}

function renderFaq() {
  const item = ([q, a]) => `<details><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`;
  el("faqList").innerHTML = FAQ[getLang()].map(item).join("");
  el("methodList").innerHTML = METHOD[getLang()].map(item).join("");
}

// ---------------------------------------------------------------- account switcher
function renderAccountButton(p) {
  el("accountAvatar").textContent = initials(p.customer.name);
  el("accountName").textContent = p.customer.name;
  el("accountMeta").textContent = `${sector(p.customer.sector)} · ${p.customer.n_devices} ${getLang() === "fi" ? "laitetta" : "machines"}`;
}
function toggleMenu(open) {
  const m = el("accountMenu");
  const show = open ?? m.classList.contains("hidden");
  m.classList.toggle("hidden", !show);
  el("accountBtn").setAttribute("aria-expanded", String(show));
  if (show) el("customerSelect").focus();
}

// ---------------------------------------------------------------- routing
const RENDER = {
  overview: (p) => { renderAnswers(p); renderHero(p); renderKpis(p); renderHowSave(p); renderProblems(p);
    renderMachinesNow(el("machinesNowOverview"), p.machines_now, { limit: 4, mode: state.mv.overview }); },
  savings: (p) => { renderSavings(p);
    costChart(p, (s) => openTrace(costStreamTrace(p, s), `${t("card.cost")} · ${stream(s)}`, `monthly.cost_by_stream.${s}`)); },
  machines: (p) => { renderMachinesNow(el("machinesNow"), p.machines_now, { mode: state.mv.machines });
    el("machinesAsOf").textContent = p.machines_now[0] ? t("machines.asof", { date: date(p.machines_now[0].as_of) }) : ""; renderMachines(p); },
  contracts: renderContracts,
  weight: (p) => { renderWeightModel(state.index.weight_model); weightChart(p); recyclingChart(p); densityChart(p); },
  trends: (p) => renderTrends(p, state.index.assumptions.target_fill_pct),
  account: renderAccount,
};

async function route() {
  const hash = (location.hash || "#overview").slice(1);
  const view = VIEWS.includes(hash) ? hash : "overview";
  state.route = view;
  state.ws = wsOf(view);
  VIEWS.forEach((v) => el(`view-${v}`).classList.toggle("hidden", v !== view));
  document.querySelectorAll("[data-ws-nav]").forEach((n) => n.classList.toggle("hidden", n.dataset.wsNav !== state.ws));
  document.querySelectorAll(".ws button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.ws === state.ws)));
  document.querySelectorAll(".navitem").forEach((a) => {
    if (a.getAttribute("href") === `#${view}`) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  el("customerPick").classList.toggle("hidden", state.ws !== "customer" || view === "faq");
  el("operatorPick").classList.toggle("hidden", state.ws !== "partners");
  el("pageTitle").textContent = t(NAV_KEY[view]);
  el("pageEyebrow").textContent = state.ws === "europress" ? t("ep.eyebrow")
    : state.ws === "partners" || view === "faq" ? "Europress SMART" : `${state.customer?.customer.name ?? ""} · ${t("top.period")}`;
  el("sidebar").classList.remove("open");
  toggleMenu(false);
  window.scrollTo({ top: 0 });
  if (state.ws === "europress") {
    setAskContext({ view: "fleet", id: "FLEET", page: view, name: "Europress" });
    const f = await getJson("/data/fleet.json");
    if (view === "ep-overview") renderEpOverview(f);
    else if (view === "ep-pipeline") { renderSalesAlerts(f, (q) => { setAskContext({ page: "ep-sales" }); openAi(q, "sales_alerts"); }); }
    if (view === "ep-pipeline") renderEpPipeline(f, (id) => { el("customerSelect").value = id; loadCustomer(id); location.hash = "#overview"; });
    else if (view === "ep-fleet") renderEpFleet(f);
    else if (view === "ep-data") renderEpData(f);
  } else if (state.ws === "partners") {
    const id = el("operatorSelect").value;
    setAskContext({ view: "operator", id, page: "operators", name: id });
    if (view === "operators") renderOperator(await getJson(`/data/operators/${id}.json`), state.index.customers);
    else renderFaq();
  } else if (view === "faq") renderFaq();
  else {
    setAskContext({ view: "customer", id: state.customer.customer.id, page: view, name: state.customer.customer.name });
    RENDER[view]?.(state.customer);
  }
}

async function loadCustomer(id) {
  state.customer = await getJson(`/data/customers/${id}.json`);
  try { localStorage.setItem("ep.customer", id); } catch { /* storage blocked */ }
  renderAccountButton(state.customer);
  if (state.ws === "customer") route();
}

function fillSelects() {
  const cs = el("customerSelect"), os = el("operatorSelect");
  const cv = cs.value, ov = os.value;
  cs.innerHTML = state.index.customers.map((c) =>
    `<option value="${c.id}">${esc(c.name)} — ${esc(sector(c.sector))} (${c.n_devices})${c.id === state.index.hero ? " ★" : ""}</option>`).join("");
  os.innerHTML = state.index.operators.map((o) => `<option value="${o.id}">${esc(o.name)}</option>`).join("");
  if (cv) cs.value = cv;
  if (ov) os.value = ov;
}

function rerenderAll() {
  applyStatic();
  syncViewToggles();
  document.querySelectorAll(".seg button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === getLang())));
  fillSelects();
  if (state.customer) renderAccountButton(state.customer);
  route();
}

function syncViewToggles() {
  document.querySelectorAll(".mv").forEach((g) => g.querySelectorAll("button").forEach((b) =>
    b.setAttribute("aria-pressed", String(b.dataset.mode === state.mv[g.dataset.mv]))));
}

function bindGlobal() {
  document.querySelectorAll(".mv").forEach((g) => g.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-mode]");
    if (!b) return;
    state.mv[g.dataset.mv] = b.dataset.mode;
    syncViewToggles();
    if (g.dataset.mv === "overview") renderMachinesNow(el("machinesNowOverview"), state.customer.machines_now, { limit: 4, mode: state.mv.overview });
    else renderMachinesNow(el("machinesNow"), state.customer.machines_now, { mode: state.mv.machines });
  }));
  el("customerSelect").addEventListener("change", (e) => { toggleMenu(false); loadCustomer(e.target.value); });
  el("operatorSelect").addEventListener("change", () => route());
  el("accountBtn").addEventListener("click", (e) => { e.stopPropagation(); toggleMenu(); });
  el("accountMenu").addEventListener("click", (e) => e.stopPropagation());
  document.addEventListener("click", () => toggleMenu(false));
  document.querySelectorAll(".seg button").forEach((b) => b.addEventListener("click", () => { setLang(b.dataset.lang); rerenderAll(); }));
  document.querySelectorAll("[data-close]").forEach((b) => b.addEventListener("click", closePanels));
  el("scrim").addEventListener("click", closePanels);
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { closePanels(); toggleMenu(false); } });
  el("menuBtn").addEventListener("click", (e) => { e.stopPropagation(); el("sidebar").classList.toggle("open"); });
  el("gauge").addEventListener("click", () => openTrace(state.customer.kpis.avg_fill, t("kpi.avg_fill"), "kpis.avg_fill"));
  el("weightWrap").addEventListener("click", () => openTrace(state.customer.weight.trace, t("card.weight"), "weight"));
  window.addEventListener("hashchange", route);
  document.querySelectorAll(".ws button").forEach((b) => b.addEventListener("click", () => { location.hash = WS_HOME[b.dataset.ws]; }));
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-info]");
    if (!b) return;
    const title = b.closest(".card")?.querySelector("h2")?.textContent || el("pageTitle").textContent;
    openInfo(title, t(b.dataset.info));
  });
}

async function init() {
  setLang(getLang());
  state.index = await getJson("/data/index.json");
  fillSelects();
  let start = state.index.hero;
  try { start = localStorage.getItem("ep.customer") || start; } catch { /* storage blocked */ }
  if (!state.index.customers.some((c) => c.id === start)) start = state.index.hero;
  el("customerSelect").value = start;
  initAi();
  setAskHandler((title, focus) => {
    closePanels();
    openAi(getLang() === "fi" ? `Selitä "${title}": miten se lasketaan ja mitä minun kannattaa tehdä?` : `Explain "${title}": how is it calculated and what should I do?`, focus);
  });
  bindGlobal();
  renderWeightModel(state.index.weight_model);
  state.customer = await getJson(`/data/customers/${start}.json`);
  rerenderAll();
}

init().catch((e) => {
  document.querySelector(".main").insertAdjacentHTML("afterbegin", `<p class="note">Could not load data: ${esc(e.message)}</p>`);
});
