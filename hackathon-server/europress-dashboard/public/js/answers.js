// "What should I do?" — ready-made answers to the customer's framework of questions.
// Level 1: one-line answer · Level 2 (click): why + numbered steps · Level 3: the full calculation / SMART Advisor.
import { t, fmt, eur, date } from "./i18n.js";
import { esc, openTrace } from "./drawer.js";
import { openAi } from "./ask.js";

const el = (id) => document.getElementById(id);
const ORDER = { bad: 0, warn: 1, info: 2, good: 3 };
const STATE = { bad: "bad", warn: "warn", info: "info", good: "good" };

function params(a) {
  const q = { ...a.p };
  for (const k of ["eur", "inv_eur"]) if (q[k] != null) q[k] = eur(q[k]);
  for (const k of ["fill", "ontime", "rate", "mixed_a", "mixed_b", "eurt", "km", "full_h", "down_h", "tiny", "inv", "wdiff", "early", "lifts", "wasted", "missed"]) if (typeof q[k] === "number") q[k] = fmt(q[k]);
  if (typeof q.co2 === "number") q.co2 = fmt(q.co2, 1);
  if (q.notice) q.notice = date(q.notice);
  return q;
}

function traceFor(p, path) {
  if (!path) return null;
  const [head, key] = path.split(".");
  if (head === "levers") return p.levers.find((l) => l.id === key)?.trace;
  if (head === "kpis") return p.kpis[key];
  if (head === "operators") return p.operators[0]?.trace;
  return null;
}

export function renderAnswers(p) {
  const list = [...(p.answers || [])].sort((a, b) => ORDER[a.status] - ORDER[b.status]);
  el("answers").innerHTML = list.map((a, i) => {
    const q = params(a);
    const head = t(`a.${a.id}.${a.status === "good" ? "good" : "head"}`, q);
    const steps = t(`a.${a.id}.steps`, q).split("|");
    return `<li class="ans" data-i="${i}" data-status="${a.status}">
      <button type="button" class="ans-row" aria-expanded="false">
        <span class="state" data-state="${STATE[a.status]}">${esc(t(`ans.${a.status}`))}</span>
        <span class="ans-q">${esc(t(`a.${a.id}.q`))}</span>
        <b class="ans-h">${esc(head)}</b>
        <span class="ans-chev" aria-hidden="true">+</span>
      </button>
      <div class="ans-more" hidden>
        <p class="ans-why">${esc(t(`a.${a.id}.why`, q))}</p>
        <ol class="ans-steps">${steps.map((s) => `<li>${esc(s.trim())}</li>`).join("")}</ol>
        <div class="ans-actions">
          ${a.trace ? `<button type="button" class="btn ghost" data-calc="${i}">${esc(t("ans.calc"))}</button>` : ""}
          <button type="button" class="ask-link" data-ask="${i}">${esc(t("ai.cta"))} →</button>
        </div>
      </div></li>`;
  }).join("");
  el("answers").querySelectorAll(".ans").forEach((li) => {
    const a = list[Number(li.dataset.i)];
    const row = li.querySelector(".ans-row"), more = li.querySelector(".ans-more");
    row.addEventListener("click", () => {
      const open = more.hidden;
      more.hidden = !open; row.setAttribute("aria-expanded", String(open));
      li.querySelector(".ans-chev").textContent = open ? "−" : "+";
    });
    li.querySelector("[data-calc]")?.addEventListener("click", () => openTrace(traceFor(p, a.trace), t(`a.${a.id}.q`), a.trace));
    li.querySelector("[data-ask]").addEventListener("click", () => openAi(t(`a.${a.id}.q`), `answers.${a.id}`));
  });
}
