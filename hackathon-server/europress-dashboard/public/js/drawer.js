// "Where does this number come from?" drawer — formula, assumption, source tables, contributing rows.
import { t, getLang, fmt } from "./i18n.js";

const el = (id) => document.getElementById(id);
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

let lastFocus = null;
let onAsk = null;
export function setAskHandler(fn) { onAsk = fn; }

export function openPanel(panel) {
  lastFocus = document.activeElement;
  el("scrim").classList.remove("hidden");
  panel.classList.remove("hidden");
  panel.querySelector("[data-close]")?.focus();
}
export function closePanels() {
  el("scrim").classList.add("hidden");
  document.querySelectorAll(".drawer").forEach((d) => d.classList.add("hidden"));
  lastFocus?.focus?.();
}

function formatValue(v, unit) {
  if (v == null) return "–";
  if (unit === "EUR" || unit === "EUR/yr") return `${fmt(v)} €${unit === "EUR/yr" ? (getLang() === "fi" ? " / v" : " / yr") : ""}`;
  if (unit === "EUR/t") return `${fmt(v)} €/t`;
  if (unit === "%") return `${fmt(v, 1)} %`;
  return `${fmt(v, Number.isInteger(v) ? 0 : 1)} ${unit}`;
}

function rowsTable(rows) {
  if (!rows?.rows?.length) return "";
  const head = rows.columns.map((c) => `<th>${esc(c)}</th>`).join("");
  const body = rows.rows.map((r) => `<tr>${r.map((v) => `<td class="${typeof v === "number" ? "num" : ""}">${esc(typeof v === "number" ? fmt(v, Number.isInteger(v) ? 0 : 2) : v)}</td>`).join("")}</tr>`).join("");
  return `<section class="drawer-section">
    <h3>${t("drawer.rows")} <span class="muted">(${t("drawer.of", { n: rows.rows.length, total: fmt(rows.total_rows) })})</span></h3>
    <div class="table-wrap"><table class="table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>
  </section>`;
}

/**
 * @param {{value:number, unit:string, formula:{en:string, fi:string}, sources:string[], rows?:object, assumption?:string}} trace
 * @param {string} title   human label of the metric
 * @param {string} focus   metric key passed to the AI ("kpis.total_cost")
 */
export function openTrace(trace, title, focus = "", todo = "") {
  if (!trace) return;
  el("drawerTitle").textContent = title;
  const formula = trace.formula?.[getLang()] || trace.formula?.en || "";
  el("drawerBody").innerHTML = `
    ${trace.value == null && !trace.unit ? "" : `<div class="drawer-value">${esc(formatValue(trace.value, trace.unit))}</div>`}
    ${todo ? `<section class="drawer-section"><h3>${t("drawer.todo")}</h3><div class="todo">${esc(todo)}</div></section>` : ""}
    <section class="drawer-section"><h3>${t("drawer.formula")}</h3><div class="formula">${esc(formula)}</div></section>
    ${trace.assumption ? `<div class="assumption"><span class="state" data-state="warn">${t("drawer.assumption")}</span><span>${esc(trace.assumption)}</span></div>` : ""}
    <section class="drawer-section"><h3>${t("drawer.sources")}</h3><div class="sources">${(trace.sources || []).map((s) => `<code>${esc(s)}</code>`).join("")}</div></section>
    ${rowsTable(trace.rows)}
    <div><button class="btn ghost" type="button" id="drawerAsk">${t("drawer.ask")}</button></div>`;
  el("drawerAsk").addEventListener("click", () => onAsk?.(title, focus));
  openPanel(el("drawer"));
}

/** Device trace built client-side from the device row. */
export function deviceTrace(d) {
  return {
    value: d.eur_per_t, unit: "EUR/t",
    formula: {
      en: `${fmt(d.cost_eur)} € invoiced ÷ ${fmt(d.tonnes, 2)} t collected over ${d.lifts} lifts. Peers (same stream, whole fleet) median: ${fmt(d.peer_median_eur_per_t)} €/t. Average fill at emptying ${fmt(d.avg_fill_pct)} %, ${d.wasted_trips} wasted trips.`,
      fi: `${fmt(d.cost_eur)} € laskutettu ÷ ${fmt(d.tonnes, 2)} t kerätty ${d.lifts} tyhjennyksessä. Vertailu (sama jae, koko laitekanta) mediaani: ${fmt(d.peer_median_eur_per_t)} €/t. Keskimääräinen täyttöaste ${fmt(d.avg_fill_pct)} %, ${d.wasted_trips} turhaa käyntiä.`,
    },
    sources: ["finance/invoice_lines.parquet", "operations/collection_events.parquet", "reference/devices.parquet"],
    rows: {
      columns: ["device_id", "site", "stream", "volume_m3", "policy", "operator_id", "lifts", "tonnes", "cost_eur", "eur_per_t", "avg_fill_pct"],
      rows: [[d.device_id, d.site, d.stream, d.volume_m3, d.policy, d.operator_id, d.lifts, d.tonnes, d.cost_eur, d.eur_per_t, d.avg_fill_pct]],
      total_rows: 1,
    },
  };
}

/** Plain explanation pop-up for the ⓘ buttons — long text lives here, not on the page. */
export function openInfo(title, text) {
  el("drawerTitle").textContent = title;
  el("drawerBody").innerHTML = `<div class="info-text">${String(text).split(/(?<=[.!?])\s+(?=[A-ZÅÄÖ0-9])/).map((p) => `<p>${esc(p)}</p>`).join("")}</div>`;
  openPanel(el("drawer"));
}
