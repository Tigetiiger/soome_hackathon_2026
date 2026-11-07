// Machine drawings: a compactor outline filled to its current level, with "full in N days".
// Forecast and weight are DEMO placeholders — production values come from Europress' SMART forecast and the weight model.
import { t, fmt, date, stream, getLang } from "./i18n.js";
import { esc } from "./drawer.js";
import { STREAM_COLORS } from "./charts.js";
import { openAi } from "./ask.js";
import { getWeightModel } from "./weightmodel.js";

const PICKUP_LINE = 85; // SMART orders the pickup automatically here — the drawing never fills above it
// What each stream means for the customer: recyclables earn a credit, mixed waste is the one to eliminate.
const KIND = { cardboard: "credit", plastic_film: "credit", mixed_plastic: "credit", paper: "recycle", biowaste: "bio", mixed_waste: "mixed" };
const KIND_STATE = { credit: "good", recycle: "info", bio: "note", mixed: "warn" };

/**
 * Side view of a Europress CombiMax-type compactor (drawn from product photos), filled to its current level.
 * Front → back: hook-lift A-frame · press unit with sloped hopper lid and control panel · tall collar frame ·
 * container with top/bottom bands, rear door, hinges and lock · skid rail with brackets and rollers.
 * Container length follows the machine's volume so 3 m³ and 12 m³ units read differently.
 */
export function compactorSvg(m, { label = true } = {}) {
  const f = Math.max(0, Math.min(PICKUP_LINE, m.fill_now ?? 0));
  const color = STREAM_COLORS[m.stream] || "currentColor";
  const v = m.volume_m3 ?? 8;
  const L = Math.round(Math.min(150, Math.max(84, 56 + v * 9)));
  const P0 = 18, C0 = 90, C1 = C0 + L;                 // press start, container start/end
  const top = 26, rise = 4, bot = 98;                  // container roof rises toward the rear
  const ox = Math.round((250 - (C1 + 12)) / 2);        // centre the drawing in the card
  const level = bot - ((bot - top) * f) / 100;
  const target = bot - (bot - top) * (PICKUP_LINE / 100);
  const id = `clip-${String(m.device_id).replace(/[^A-Za-z0-9_-]/g, "")}`;
  const shell = `M${C0} ${top}L${C1 - 7} ${top - rise}L${C1} ${top - rise + 7}V${bot}H${C0}Z`;
  const brackets = Array.from({ length: Math.floor((C1 - P0) / 26) }, (_, i) =>
    `<rect x="${P0 + 8 + i * 26}" y="${bot + 6}" width="7" height="3" class="mc-dark"/>`).join("");
  return `<svg class="mc-svg" viewBox="0 0 250 118" ${label ? `role="img" aria-label="${esc(m.device_id)} ${fmt(f)} %"` : 'aria-hidden="true"'}>
    <defs><clipPath id="${id}"><path d="${shell}"/></clipPath>
      <pattern id="${id}-h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="mc-hatch"/></pattern></defs>
    <g transform="translate(${ox} 0)">
      <!-- underframe: skid rail, brackets, hook-lift rollers -->
      <rect x="${P0 - 10}" y="${bot}" width="${C1 + 4 - (P0 - 10)}" height="6" class="mc-press"/>
      ${brackets}
      <circle cx="${P0 - 5}" cy="${bot + 9}" r="5" class="mc-dark"/><circle cx="${C1 - 2}" cy="${bot + 9}" r="5" class="mc-dark"/>
      <!-- hook-lift A-frame with hook -->
      <rect x="${P0 - 10}" y="52" width="7" height="${bot - 52}" class="mc-press"/>
      <path d="M${P0 - 6.5} 52v-5a4 4 0 1 1 8 0v3" class="mc-line"/>
      <!-- press unit: sloped hopper lid, service door, control panel with E-stop -->
      <path d="M${P0} ${bot}V60L${C0 - 10} 46V${bot}Z" class="mc-press"/>
      <path d="M${P0 - 3} 59.5L${C0 - 10} 44.5" class="mc-lid"/>
      <line x1="${P0}" x2="${C0 - 10}" y1="84" y2="84" class="mc-line"/>
      <rect x="${P0 + 5}" y="65" width="14" height="27" rx="1" class="mc-line"/>
      <rect x="${P0 + 26}" y="63" width="25" height="14" rx="2" class="mc-dark"/>
      <circle cx="${P0 + 32}" cy="70" r="2.6" class="mc-socket"/><circle cx="${P0 + 44}" cy="70" r="3.2" class="mc-estop"/>
      <!-- container fill level + SMART target -->
      <g clip-path="url(#${id})">
        <rect x="${C0}" y="${level}" width="${L}" height="${bot - level}" class="mc-fill" style="fill:${color}"/>
        ${m.stream === "mixed_waste" ? `<rect x="${C0}" y="${level}" width="${L}" height="${bot - level}" fill="url(#${id}-h)"/>` : ""}
      </g>
      <line x1="${C0}" x2="${C1}" y1="${target}" y2="${target}" class="mc-pickup"/>
      <text x="${C0 + 4}" y="${target - 3}" class="mc-pickup-label">${PICKUP_LINE} %</text>
      <!-- container shell, bands, rear door, hinges, lock -->
      <path d="${shell}" class="mc-body"/>
      <path d="M${C0} ${top + 7}L${C1 - 7} ${top - rise + 7}H${C1}" class="mc-line"/>
      <line x1="${C0}" x2="${C1}" y1="${bot - 9}" y2="${bot - 9}" class="mc-line"/>
      <line x1="${C1 - 15}" x2="${C1 - 15}" y1="${top - rise + 2}" y2="${bot}" class="mc-line"/>
      <rect x="${C1 - 1}" y="34" width="4" height="7" class="mc-dark"/><rect x="${C1 - 1}" y="62" width="4" height="7" class="mc-dark"/><rect x="${C1 - 1}" y="84" width="4" height="7" class="mc-dark"/>
      <rect x="${C1 - 11}" y="55" width="6" height="11" rx="1" class="mc-line"/>
      <!-- collar frame between press and container (stands above both) -->
      <rect x="${C0 - 10}" y="14" width="10" height="${bot - 14}" class="mc-press"/>
    </g>
  </svg>`;
}

const TRUCK_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 6.5h11v9h-11zM13.5 9.5h4l3 3v3h-7"/><circle cx="6.5" cy="17" r="1.8"/><circle cx="17" cy="17" r="1.8"/></svg>';
const loc = () => (getLang() === "fi" ? "fi-FI" : "en-GB");
const fmtDay = (iso) => new Intl.DateTimeFormat(loc(), { weekday: "short", day: "numeric", month: "short" }).format(new Date(`${iso}T12:00:00`));
let asOf = null; // status date of the data ("today" in the demo)
const dayDate = (iso) => (iso === asOf ? t("m.today") : fmtDay(iso));
const weekday = (i) => new Intl.DateTimeFormat(loc(), { weekday: "long" }).format(new Date(2024, 0, 1 + i)); // 2024-01-01 = Monday

function scheduleText(m) {
  const days = String(m.schedule_weekdays || "").split(",").filter((x) => x.trim() !== "").map((x) => weekday(Number(x)));
  const list = days.join(t("sched.and"));
  const step = Math.max(1, Math.round(days.length / (m.schedule_per_week || days.length || 1)));
  if (step === 1) return t("sched.every", { days: list });
  if (step === 2) return t("sched.everyOther", { days: list });
  return t("sched.everyN", { n: step, days: list });
}

/** Who sends the truck and when: SMART on-call order, or the operator's fixed timetable. */
function truckBlock(m) {
  const op = esc(m.operator || m.operator_id || "");
  const lines = [];
  let state = "mute";
  if (m.policy === "ON_CALL") {
    if (m.pickup_ordered) { lines.push(t("truck.ordered", { op })); state = "info"; }
    else if (m.order_on) lines.push(t(m.pickup_reason === "interval" ? "truck.willOrderInterval" : "truck.willOrder", { op, date: dayDate(m.order_on), thr: fmt(m.order_threshold_pct) }));
    else lines.push(t("m.notSoon"));
    if (m.truck_on) lines.push(t("truck.eta", { date: dayDate(m.truck_on), h: fmt(m.lead_h) }));
    if ((m.days_to_pickup ?? 99) <= 2) state = "info";
  } else {
    lines.push(t("truck.fixed", { op, sched: esc(scheduleText(m)) }));
    if (m.truck_on) lines.push(t("truck.next", { date: dayDate(m.truck_on), fill: m.visit_fill_pct > PICKUP_LINE ? `≥ ${PICKUP_LINE}` : `≈ ${fmt(m.visit_fill_pct)}` }));
  }
  const early = m.policy !== "ON_CALL" && m.visit_fill_pct != null && m.visit_fill_pct < 60;
  const lowThr = m.policy === "ON_CALL" && m.stream !== "biowaste" && m.order_threshold_pct != null && m.order_threshold_pct < 75;
  return `<div class="mc-truck" data-state="${early ? "warn" : state}">
      <span class="mc-truck-ic">${TRUCK_ICON}</span>
      <div>${lines.map((l, i) => `<p class="${i ? "mc-truck-sub" : "mc-truck-main"}">${l}</p>`).join("")}
        ${early ? `<p class="mc-tip"><span class="state" data-state="warn">${esc(t("truck.early"))}</span></p>` : ""}
        ${lowThr ? `<p class="mc-tip"><span class="state" data-state="warn">${esc(t("truck.thr", { thr: fmt(m.order_threshold_pct) }))}</span></p>` : ""}
        ${m.operator_on_time_pct != null ? `<p class="mc-truck-sub">${t("truck.onTime", { op, pct: fmt(m.operator_on_time_pct) })}</p>` : ""}
      </div></div>`;
}

function typeTag(m) {
  const kind = KIND[m.stream] || "recycle";
  return `<span class="state" data-state="${KIND_STATE[kind]}">${esc(t(`kind.${kind}`))}</span>`;
}
const modelKg = (m) => { const v = getWeightModel(); return m.weight_by_model && v && m.weight_by_model[v] != null ? m.weight_by_model[v] : m.weight_kg_now; };
const weightLine = (m) => (modelKg(m) != null ? `${t("m.weight", { kg: fmt(modelKg(m)) })} <span class="demo">${esc(getWeightModel() || t("m.demo"))}${m.weight_by_model && !m.weight_by_model.calibrated && getWeightModel() === "v3" ? ` · ${esc(t("wm.notCal"))}` : ""}</span>` : "–");
const mixedAsk = (m) => (KIND[m.stream] === "mixed" ? `<button type="button" class="ask-link" data-mixed="${esc(m.device_id)}">${esc(t("m.askMixed"))}</button>` : "");
const howScheduled = (m) => (m.policy === "ON_CALL" ? t("mv.onCall", { thr: fmt(m.order_threshold_pct) }) : t("mv.timetable", { sched: scheduleText(m) }));

/** "design": drawing cards · "mixed": small drawing + info table per machine · "table": plain table. */
const VIEW = {
  design: (rows) => rows.map((m) => `<article class="machine" data-kind="${KIND[m.stream] || "recycle"}">
      ${compactorSvg(m)}
      <div class="mc-head"><b>${fmt(m.fill_now)}&nbsp;%</b>${typeTag(m)}</div>
      ${truckBlock(m)}
      <p class="mc-meta"><span class="dot" style="background:${STREAM_COLORS[m.stream]}"></span>${esc(stream(m.stream))} · ${fmt(m.volume_m3)} m³ · ${esc(m.device_id)}</p>
      <p class="mc-meta">${modelKg(m) != null ? weightLine(m) : ""}</p>
      ${mixedAsk(m)}
    </article>`).join(""),
  mixed: (rows) => rows.map((m) => `<article class="mrow" data-kind="${KIND[m.stream] || "recycle"}">
      <div class="mrow-fig">${compactorSvg(m)}<b class="mrow-fill">${fmt(m.fill_now)}&nbsp;%</b></div>
      <dl class="mrow-dl">
        <div><dt>${t("col.machine")}</dt><dd>${esc(m.device_id)} · ${esc(m.site)}</dd></div>
        <div><dt>${t("col.stream")}</dt><dd><span class="dot" style="background:${STREAM_COLORS[m.stream]}"></span>${esc(stream(m.stream))} · ${fmt(m.volume_m3)} m³ ${typeTag(m)}</dd></div>
        <div><dt>${t("mv.scheduling")}</dt><dd>${esc(howScheduled(m))}</dd></div>
        <div><dt>${t("col.operator")}</dt><dd>${esc(m.operator || "–")}${m.operator_on_time_pct != null ? ` · ${t("mv.onTime", { pct: fmt(m.operator_on_time_pct) })}` : ""}</dd></div>
        <div class="span2"><dt>${t("mv.nextTruck")}</dt><dd>${truckBlock(m)}</dd></div>
        <div><dt>${t("mv.weight")}</dt><dd>${weightLine(m)}</dd></div>
        <div><dt>${t("mv.fillRate")}</dt><dd>${m.fill_rate_per_day != null ? t("mv.perDay", { v: fmt(m.fill_rate_per_day, 1) }) : "–"}</dd></div>
      </dl>
      ${mixedAsk(m)}
    </article>`).join(""),
  table: (rows) => `<div class="table-wrap"><table class="table"><thead><tr>
      <th>${t("col.machine")}</th><th>${t("col.stream")}</th><th class="num">${t("mv.fillNow")}</th><th>${t("mv.scheduling")}</th>
      <th>${t("col.operator")}</th><th>${t("mv.nextTruck")}</th><th class="num">${t("mv.fillAtVisit")}</th><th class="num">${t("mv.weight")}</th></tr></thead><tbody>${
    rows.map((m) => `<tr>
      <td class="strong">${esc(m.device_id)}<span class="desc">${esc(m.site)} · ${fmt(m.volume_m3)} m³</span></td>
      <td><span class="dot" style="background:${STREAM_COLORS[m.stream]}"></span>${esc(stream(m.stream))}</td>
      <td class="num">${fmt(m.fill_now)} %</td>
      <td>${esc(howScheduled(m))}</td>
      <td>${esc(m.operator || "–")}</td>
      <td>${m.pickup_ordered ? esc(t("mv.ordered")) : m.truck_on ? esc(dayDate(m.truck_on)) : "–"}</td>
      <td class="num">${m.visit_fill_pct == null ? "–" : m.visit_fill_pct > PICKUP_LINE ? `≥ ${PICKUP_LINE} %` : `${fmt(m.visit_fill_pct)} %`}</td>
      <td class="num">${modelKg(m) != null ? `${fmt(modelKg(m))} kg` : "–"}</td></tr>`).join("")}</tbody></table></div>`,
};

export function renderMachinesNow(container, list, { limit = Infinity, mode = "design" } = {}) {
  asOf = list[0]?.as_of ?? null;
  const rows = [...list].sort((a, b) => (a.days_to_pickup ?? 999) - (b.days_to_pickup ?? 999)).slice(0, limit);
  container.dataset.mode = mode;
  container.innerHTML = (VIEW[mode] || VIEW.design)(rows);
  container.querySelectorAll("[data-mixed]").forEach((b) =>
    b.addEventListener("click", () => openAi(t("q.mixedMachine", { id: b.dataset.mixed }), `machines.${b.dataset.mixed}`)));
}
