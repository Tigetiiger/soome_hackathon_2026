#!/usr/bin/env bash
# Reproduce every number in docs/agents/data-analyst.md.  Python: /home/hackathon/.claude/jobs/717fee2a/tmp/v/bin/python (pandas, duckdb, sklearn, scipy)
# Dataset (read-only): /home/hackathon/europress_data/Europress_SMART_Material_Value_Engine_v1.0.1/data/competition/public   Seed: 20261106 (common.py)
set -euo pipefail
cd "$(dirname "$0")"
# Interpreter: override with PY=..., else the project .venv (python3 -m venv .venv && pip install -r requirements.txt), else python3
PY="${PY:-$( [ -x ../.venv/bin/python ] && echo "$(cd .. && pwd)/.venv/bin/python" || echo python3 )}"
# 0. reference baselines B1-B6 (copy of the dataset's own code, scores on public validation labels; ~11 min)
[ -d baseline_run/reports ] || (cd baseline_run && $PY -I baselines/run_all.py competition > ../outputs/baselines_run.log 2>&1)
$PY -I 00_cache_telemetry.py                      # dedup telemetry -> outputs/telemetry_dedup.parquet (git-ignored)
$PY -I 01_weight_disagreement.py       | tee outputs/01_run.log    # Q1 disagreement + causes + EUR basis effect
$PY -I 02_invoice_value_and_eurt_coverage.py | tee outputs/02_run.log  # Q2 invoice discrepancy EUR, Q3 EUR/t coverage
$PY -I 03_unnecessary_lifts_s39_s40.py | tee outputs/03_run.log    # Q4 S39/S40 weight beyond fill
$PY -I 04_density_contamination_moisture.py | tee outputs/04_run.log  # Q5 density / contamination / moisture
$PY -I 05_operator_scorecard_c2.py     | tee outputs/05_run.log    # Q6 scorecard + C2 pool
$PY -I 05c_scorecard_weight_bias.py    | tee outputs/05c_run.log   # Q6 neutral vs naive operator weight bias
# C2 mass-source ablation and hypothetical-sigma runs (each ~3-4 min; 3 in parallel)
printf "none\nno_weight\nno_device\ndefault\ndevice_only\noracle\nsim:0.5\nsim:1\nsim:1.5\nsim:3\nsim:5\nsim:10\n" | xargs -P 3 -I{} sh -c "$PY -I 05b_c2_mass_ablation.py {} > outputs/05b_\$(echo {} | tr ':' '_').log 2>&1"
$PY -I 06_accuracy_sensitivity.py      | tee outputs/06_run.log    # Q7 value vs sigma (needs 03 and 05b)
$PY -I 07_rules_vs_ml.py               | tee outputs/08_run.log    # rules vs ML
$PY -I 08_decisions_mass_trigger.py    | tee outputs/09_run.log    # mass-target trigger value (Task C context)
$PY -I 09_value_pool_summary.py        | tee outputs/09_summary.log
$PY -I 10_sql_crosschecks.py           | tee outputs/10_sql.log
