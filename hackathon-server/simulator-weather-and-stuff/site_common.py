"""Shared helpers for the static results site: inputs bookkeeping, formatting, tiny markdown, figures."""
from __future__ import annotations

import json
import logging
import math
import re
import shutil
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
GOOD_PCT = 5.0
SPLIT_LABEL = {"bins": "unseen machines", "time": "same machines, later months"}
CAPTIONS = {
    "lifts": "Lifted mass per material (left) and days between lifts (right).",
    "temperature": "Monthly mean temperature per region (synthetic weather).",
    "weather_effect": "Cardboard lift mass in wet & humid vs dry weeks, by infeed type (machine-normalised).",
    "pressure_vs_fill": "Hourly peak ram pressure vs true fill, coloured by true pack density.",
    "pressure_graph": "Per-stroke pressure graphs of one machine, coloured by true fill: the contact point moves "
                      "earlier in the stroke as the container fills.",
    "pressure_examples": "Example pressure graphs at low, medium and high true fill (generated for this page).",
    "fill_estimate": "Firmware fill estimate (fill_pct) vs true fill (generated for this page).",
    "ladder": "Comparison ladder: what each signal adds.",
    "learning_curve": "Error at lift vs number of training machines.",
    "lift_error_by_material": "Error at lift by material.",
    "coverage_by_material": "80 % interval coverage by material.",
    "pred_vs_true": "Predicted vs true mass at lift",
    "mass_curves": "Hourly mass estimate with interval over the test period",
    "feature_importance": "Feature importance (gain)",
    "shap": "SHAP summary at lift",
}

CSS = """
:root{--bg:#f7f8fa;--fg:#1d2330;--muted:#5d6676;--card:#fff;--line:#dde1e8;--accent:#1f6feb;
--good:#d8f3dc;--good-fg:#14532d;--code:#eef1f5;--nav:rgba(255,255,255,.92)}
@media (prefers-color-scheme:dark){:root{--bg:#0f1318;--fg:#e4e8ee;--muted:#9aa4b2;--card:#181e26;
--line:#2c3440;--accent:#6ea8fe;--good:#173b26;--good-fg:#9be3b0;--code:#212a35;--nav:rgba(15,19,24,.92)}}
*{box-sizing:border-box}html{scroll-padding-top:4rem}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
nav{position:sticky;top:0;z-index:10;background:var(--nav);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
nav ul{display:flex;gap:1.2rem;margin:0 auto;padding:.7rem 16px;list-style:none;max-width:1100px;overflow-x:auto;white-space:nowrap}
nav a{color:var(--fg);text-decoration:none;font-weight:600;font-size:.95rem}nav a:hover{color:var(--accent)}
main{max-width:1100px;margin:0 auto;padding:0 16px 3rem}section{padding-top:2.2rem}
h1{font-size:clamp(1.6rem,4vw,2.4rem);line-height:1.2;margin:.4rem 0}h2{border-bottom:1px solid var(--line);padding-bottom:.3rem}
a{color:var(--accent)}p,li{max-width:75ch}.muted{color:var(--muted)}
.disclaimer{display:inline-block;background:var(--code);border-left:4px solid var(--accent);padding:.4rem .8rem;border-radius:4px}
.note{color:var(--muted);font-style:italic;border:1px dashed var(--line);padding:.5rem .8rem;border-radius:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));gap:.8rem;margin:1.2rem 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.9rem 1rem}
.kpi b{display:block;font-size:1.7rem;line-height:1.2}.kpi span{color:var(--muted);font-size:.88rem}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr));gap:1rem}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.6rem}
img{max-width:100%;height:auto;display:block;margin:0 auto;background:#fff;border-radius:4px}
figcaption{font-size:.88rem;color:var(--muted);margin-top:.4rem}.tbl{overflow-x:auto;margin:.8rem 0}
table{border-collapse:collapse;font-size:.9rem;background:var(--card);min-width:50%}
th,td{border:1px solid var(--line);padding:.35rem .6rem;text-align:right}th{background:var(--code)}
td:first-child,th:first-child{text-align:left}td.good{background:var(--good);color:var(--good-fg);font-weight:600}
code{background:var(--code);padding:.1rem .3rem;border-radius:4px;font-size:.9em}
pre{background:var(--code);padding:.8rem;border-radius:6px;overflow-x:auto}pre code{padding:0}
.md{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.2rem 1.2rem;overflow-wrap:anywhere}
blockquote{margin:1rem 0;padding:.4rem 1rem;border-left:4px solid var(--accent);background:var(--code)}
.flow{display:flex;flex-wrap:wrap;align-items:stretch;gap:.4rem;margin:1rem 0}
.flow .box{flex:1 1 180px;background:var(--card);border:1px solid var(--line);border-top:4px solid var(--accent);
border-radius:10px;padding:.6rem .8rem;font-size:.88rem}.flow .box b{display:block;font-size:1rem;margin-bottom:.2rem}
.flow .box ul{margin:.2rem 0;padding-left:1.1rem}.flow .arrow{align-self:center;font-size:1.6rem;color:var(--muted)}
@media (max-width:760px){.flow{flex-direction:column}.flow .arrow{transform:rotate(90deg);text-align:center}}
.bars{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:1rem}
.bar-card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.6rem .8rem}
.bar-card h5{margin:.1rem 0 .5rem;font-size:.95rem}.bar{display:grid;grid-template-columns:11rem 1fr 3.2rem;
gap:.4rem;align-items:center;font-size:.8rem;margin:.15rem 0}.bar code{font-size:.78rem;overflow:hidden;text-overflow:ellipsis}
.bar .track{background:var(--code);border-radius:3px;height:.8rem}.bar .fill{background:var(--accent);height:100%;border-radius:3px}
.bar span{text-align:right;color:var(--muted)}td.l,th.l{text-align:left}
th.lift,td.lift{background:var(--good);color:var(--good-fg)}tr.key td{font-weight:700}tr.fam td{background:var(--code);font-weight:700;text-align:left}
details{margin:.6rem 0}summary{cursor:pointer;font-weight:600}.sub{font-size:1.05rem;margin-top:1.6rem}
.banner{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:6px;padding:.5rem .8rem}
.lb{position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.88);display:flex;flex-direction:column;
align-items:center;justify-content:center;padding:16px;cursor:zoom-out}.lb[hidden]{display:none}
.lb img{max-width:100%;max-height:calc(100vh - 7rem);object-fit:contain;background:#fff;border-radius:6px}
.lb-x{position:fixed;top:12px;right:12px;width:3rem;height:3rem;border-radius:50%;border:0;background:#fff;
color:#000;font-size:1.8rem;line-height:1;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.4)}
.lb-cap{color:#eee;font-size:.9rem;margin:.6rem 0 0;text-align:center;max-width:90ch}.lb-cap a{color:#9cc8ff}
a.zoom img{cursor:zoom-in}
footer{border-top:1px solid var(--line);margin-top:2rem;padding-top:1rem;font-size:.85rem;color:var(--muted)}
"""


@dataclass
class Build:
    """Tracks which inputs were used or missing during the build."""
    used: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    def check(self, rel: Path) -> Path | None:
        path = ROOT / rel
        (self.used if path.exists() else self.missing).append(str(rel))
        return path if path.exists() else None


# ---------------------------------------------------------------- formatting
def num(v: Any, nd: int = 1) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "–"
    return "–" if math.isnan(f) else f"{f:,.{nd}f}"


def sci(v: Any) -> str:
    return "–" if num(v) == "–" else f"{float(v):.1e}"


def pct_of(frac: Any, nd: int = 1) -> str:
    return "–" if num(frac) == "–" else num(float(frac) * 100, nd)


def dig(d: Any, *keys: str) -> Any:
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def note(text: str) -> str:
    return f'<p class="note">{escape(text)}</p>'


def table(header: list[str], rows: list[list[str]], good_cols: set[int] | None = None) -> str:
    """Cells are pre-formatted strings; numeric cells in good_cols < GOOD_PCT are highlighted."""
    head = "".join(f"<th>{escape(h)}</th>" for h in header)
    body = []
    for row in rows:
        cells = []
        for i, c in enumerate(row):
            hit = good_cols and i in good_cols and _below(c, GOOD_PCT)
            cells.append(f'<td{" class=good" if hit else ""}>{escape(c)}</td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def _below(cell: str, limit: float) -> bool:
    try:
        return float(cell.replace(",", "")) < limit
    except ValueError:
        return False


def _read(b: Build, rel: Path, reader: Any) -> Any:
    path = b.check(rel)
    try:
        return None if path is None else reader(path)
    except (OSError, ValueError) as exc:  # JSONDecodeError is a ValueError
        logging.warning("cannot read %s: %s", rel, exc)
        return None


def load_json(b: Build, rel: Path) -> dict | None:
    return _read(b, rel, lambda p: json.loads(p.read_text()))


def load_csv(b: Build, rel: Path) -> pd.DataFrame | None:
    return _read(b, rel, pd.read_csv)


# ---------------------------------------------------------------- tiny markdown
def md_inline(text: str) -> str:
    codes: list[str] = []

    def stash(m: re.Match) -> str:
        codes.append(f"<code>{m.group(1)}</code>")
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", stash, escape(text))
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1" loading="lazy">', s)
    s = re.sub(r"\[([^\]]+)\]\(((?:https?://|#)[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\[([^\]]+)\]\([^)\s]+\)", r"\1", s)  # local file links: keep text only
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)


def md_to_html(md: str) -> str:
    """Headings, fenced code, tables, flat lists, paragraphs, inline bold/em/code/links/images."""
    out: list[str] = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
        elif line.startswith(">"):
            j = i
            while j < len(lines) and lines[j].startswith(">"):
                j += 1
            out.append("<blockquote>" + md_inline(" ".join(x.lstrip("> ") for x in lines[i:j])) + "</blockquote>")
            i = j
        elif m := re.match(r"(#{1,6})\s+(.*)", line):
            out.append(f"<h{len(m.group(1))}>{md_inline(m.group(2))}</h{len(m.group(1))}>")
            i += 1
        elif line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            i = _md_table(lines, i, out)
        elif re.match(r"\s*([*-]|\d+\.)\s+", line):
            i = _md_list(lines, i, out)
        elif not line.strip():
            i += 1
        else:
            j = i
            while j < len(lines) and lines[j].strip() and not re.match(r"(#|>|```|\s*\||\s*([*-]|\d+\.)\s)", lines[j]):
                j += 1
            j = max(j, i + 1)
            out.append("<p>" + md_inline(" ".join(lines[i:j])) + "</p>")
            i = j
    return "\n".join(out)


def _md_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _md_table(lines: list[str], i: int, out: list[str]) -> int:
    head = "".join(f"<th>{md_inline(c)}</th>" for c in _md_cells(lines[i]))
    j, rows = i + 2, []
    while j < len(lines) and lines[j].lstrip().startswith("|"):
        rows.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in _md_cells(lines[j])) + "</tr>")
        j += 1
    out.append(f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    return j


def _md_list(lines: list[str], i: int, out: list[str]) -> int:
    tag = "ol" if re.match(r"\s*\d+\.", lines[i]) else "ul"
    items: list[str] = []
    j = i
    while j < len(lines) and lines[j].strip():
        m = re.match(r"\s*(?:[*-]|\d+\.)\s+(.*)", lines[j])
        if m:
            items.append(m.group(1))
        elif items and lines[j].startswith((" ", "\t")):
            items[-1] += " " + lines[j].strip()
        else:
            break
        j += 1
    out.append(f"<{tag}>" + "".join(f"<li>{md_inline(t)}</li>" for t in items) + f"</{tag}>")
    return j


# ---------------------------------------------------------------- images
def copy_plots(b: Build, rel_dir: Path) -> list[Path]:
    """Copy rel_dir/*.png into site/rel_dir; return site-relative paths."""
    src = b.check(rel_dir)
    if src is None:
        return []
    dest = SITE / rel_dir
    dest.mkdir(parents=True, exist_ok=True)
    pngs = sorted(src.glob("*.png"))
    for p in pngs:
        shutil.copy2(p, dest / p.name)
    return [rel_dir / p.name for p in pngs]


def caption(stem: str) -> str:
    base, _, split = stem.rpartition("_")
    if base in CAPTIONS and split in SPLIT_LABEL:
        return f"{CAPTIONS[base]} — {SPLIT_LABEL[split]} ({split} split)."
    return CAPTIONS.get(stem, stem.replace("_", " "))


def figures(paths: list[Path]) -> str:
    if not paths:
        return note("Plots not generated yet.")
    figs = [
        f'<figure><a class="zoom" href="{escape(p.as_posix())}" data-cap="{escape(caption(p.stem))}"><img src="{escape(p.as_posix())}" alt="{escape(p.stem)}" '
        f'loading="lazy"></a><figcaption>{escape(caption(p.stem))}</figcaption></figure>'
        for p in paths
    ]
    return f'<div class="figs">{"".join(figs)}</div>'


LIGHTBOX = """<div id="lb" class="lb" hidden role="dialog" aria-modal="true" aria-label="Enlarged image">
<button class="lb-x" type="button" aria-label="Close image">&times;</button><img alt="">
<p class="lb-cap"><span></span> · <a target="_blank" rel="noopener">open full size</a> · click anywhere or press Esc
to close</p></div>
<script>(function(){var lb=document.getElementById("lb");if(!lb)return;var im=lb.querySelector("img"),
cap=lb.querySelector(".lb-cap span"),full=lb.querySelector(".lb-cap a"),last=null;
function close(){lb.hidden=true;im.removeAttribute("src");document.body.style.overflow="";if(last)last.focus();}
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a.zoom");
if(a&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey){e.preventDefault();last=a;im.src=a.getAttribute("href");
im.alt=a.dataset.cap||"";cap.textContent=a.dataset.cap||"";full.href=a.getAttribute("href");lb.hidden=false;
document.body.style.overflow="hidden";lb.querySelector(".lb-x").focus();return;}
if(!lb.hidden&&!(e.target.closest&&e.target.closest(".lb-cap a")))close();});
document.addEventListener("keydown",function(e){if(!lb.hidden&&e.key==="Escape")close();});})();</script>"""


def page(title: str, body: str, nav: str = "") -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title>'
            f"<style>{CSS}</style></head><body>{nav}{body}{LIGHTBOX}</body></html>")


def pre(text: str) -> str:
    """A formula / code block (text is escaped)."""
    return f"<pre><code>{escape(text.strip(chr(10)))}</code></pre>"


def raw_table(header: list[str], rows: list[list[str]], left_cols: set[int] | None = None,
              row_class: list[str] | None = None, col_class: list[str] | None = None) -> str:
    """Like table() but cells are trusted HTML (callers escape their own text)."""
    left = left_cols or {0}
    cc = col_class or [""] * len(header)

    def cls(i: int) -> str:
        names = " ".join(x for x in ("l" if i in left else "", cc[i] if i < len(cc) else "") if x)
        return f' class="{names}"' if names else ""
    head = "".join(f"<th{cls(i)}>{h}</th>" for i, h in enumerate(header))
    body = []
    for r, row in enumerate(rows):
        rc = f' class="{row_class[r]}"' if row_class and row_class[r] else ""
        body.append(f"<tr{rc}>" + "".join(f"<td{cls(i)}>{c}</td>" for i, c in enumerate(row)) + "</tr>")
    return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def load_yaml(b: Build, rel: Path) -> dict | None:
    import yaml  # local: only the simulation section needs it

    def reader(p: Path) -> dict:
        try:
            return yaml.safe_load(p.read_text())
        except yaml.YAMLError as exc:
            raise ValueError(str(exc)) from exc
    return _read(b, rel, reader)
