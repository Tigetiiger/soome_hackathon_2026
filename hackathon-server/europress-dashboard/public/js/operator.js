// "For waste operators" view: forecast workload, expected tonnes, fill-at-pickup, renewals.
import { t, fmt, date, sector, addStrings } from "./i18n.js";
import { opStreamChart, histChart, regionChart } from "./charts.js";
import { esc, openTrace } from "./drawer.js";

const el = (id) => document.getElementById(id);

function kpi(icon, label, value, sub, onClick) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "kpi";
  b.innerHTML = `<div class="kpi-label"><span>${esc(label)}</span>${onClick ? '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4-4"/></svg>' : ""}</div>
    <div class="kpi-value">${value}</div><div class="kpi-sub">${esc(sub || "")}</div>`;
  if (onClick) b.addEventListener("click", onClick); else b.disabled = true;
  return b;
}

function workload(o) {
  const pickups = o.forecast_per_day.pickups;
  const max = Math.max(...pickups, 1);
  el("workload").innerHTML = pickups.map((n, i) => {
    const dots = Array.from({ length: Math.min(n, 9) }, () => '<span class="wl-dot"></span>').join("");
    const day = i === 0 ? t("day.today") : t("day.d", { n: i });
    return `<div class="wl-col ${n === max && n > 0 ? "peak" : ""}" title="${fmt(o.forecast_per_day.tonnes[i], 1)} t">
      <span class="wl-day">${esc(day)}</span><span class="wl-t">${fmt(o.forecast_per_day.tonnes[i], 0)} t</span>${dots}${n ? `<span class="wl-top">${n}</span>` : ""}</div>`;
  }).join("");
}

export function renderOperator(o, customers) {
  const names = Object.fromEntries(customers.map((c) => [c.id, c]));
  const total = o.forecast_per_day.pickups.reduce((a, b) => a + b, 0);
  const k = el("opKpis");
  k.replaceChildren(
    kpi("i-space", t("op.devices"), fmt(o.operator.devices), `${o.operator.regions}`),
    kpi("i-mint", t("op.forecast"), fmt(total), `${fmt(o.forecast_per_day.tonnes.reduce((a, b) => a + b, 0), 0)} t`,
        () => openTrace(o.forecast_trace, t("op.forecast"), "forecast")),
    kpi("i-amber", t("op.early"), `${fmt(o.early_lift_share.value, 1)}<small>%</small>`, t("top.period"),
        () => openTrace(o.early_lift_share, t("op.early"), "early_lift_share")),
    kpi("i-red", t("op.wasted"), fmt(o.wasted_trips), `${fmt(o.operator.customers)} ${t("op.customers").toLowerCase()}`),
  );
  workload(o);
  opStreamChart(o);
  histChart("opHistChart", o.fill_at_pickup_hist);
  if (o.extras) {
    regionChart("opRegionChart", o.extras.monthly_inbound_by_region);
    el("opHotspots").innerHTML = `<thead><tr><th>${t("top.customer")}</th><th class="num">${t("col.loads")}</th><th class="num">${t("col.cr")}</th></tr></thead>
      <tbody>${o.extras.quality_hotspots.map((h) => {
        const c = names[h.customer_id];
        return `<tr><td class="strong">${esc(c ? c.name : h.customer_id)}<span class="desc">${esc(c ? sector(c.sector) : "")}</span></td>
          <td class="num">${h.loads}</td><td class="num"><span class="state" data-state="${h.share >= 8 ? "bad" : "warn"}">${fmt(h.share, 1)} %</span></td></tr>`;
      }).join("")}</tbody>`;
  }
  const rows = o.renewals_12m.map((r) => {
    const c = names[r.customer_id];
    return `<tr><td class="strong">${esc(c ? c.name : r.customer_id)}<span class="desc">${esc(c ? sector(c.sector) : "")}</span></td>
      <td class="num">${r.contracts}</td><td class="num">${esc(date(r.renewal))}</td></tr>`;
  }).join("");
  el("renewalsTable").innerHTML = `<thead><tr><th>${t("top.customer")}</th><th class="num">${t("col.contracts")}</th><th class="num">${t("op.renewal")}</th></tr></thead><tbody>${rows}</tbody>`;
}
