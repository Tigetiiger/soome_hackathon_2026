#!/usr/bin/env bash
# Compactor pipeline: sim -> validate -> baseline -> train -> predict -> report -> site.
# Runs inside the OpenShift Job (pipeline-job.yaml); also runnable locally for testing.
#
# Settings (env, all optional):
#   RUN_NAME   main run folder under runs/ and models/     (default full400)
#   BINS       compactors in the main run                   (default 400)
#   DAYS       days simulated                               (default 365)
#   SEED       random seed                                  (default 7)
#   SMALL_RUN  1 = also simulate + train runs/bins25        (default 1; the site compares both)
#   STEPS      steps to run, in this order                  (default: all seven)
#   DATA_DIR   persistent volume; runs/ models/ site/ link here (default /data)
#   PYTHON     interpreter                                  (default python)
set -euo pipefail

RUN_NAME="${RUN_NAME:-full400}"
BINS="${BINS:-400}"
DAYS="${DAYS:-365}"
SEED="${SEED:-7}"
SMALL_RUN="${SMALL_RUN:-1}"
ALL_STEPS="sim validate baseline train predict report site"
STEPS="${STEPS:-$ALL_STEPS}"
DATA_DIR="${DATA_DIR:-/data}"
PY="${PYTHON:-python}"
SMALL_NAME=bins25
SMALL_BINS=25

fail() { echo "pipeline: $*" >&2; exit 2; }

[[ "$RUN_NAME" =~ ^[A-Za-z0-9._-]+$ ]] || fail "RUN_NAME must be a plain folder name, got '$RUN_NAME'"
for s in $STEPS; do
  [[ " $ALL_STEPS " == *" $s "* ]] || fail "unknown step '$s' (valid: $ALL_STEPS)"
done

cd "$(dirname "$0")/../.."
mkdir -p "$DATA_DIR"/{runs,models,site,logs}
LOG="$DATA_DIR/logs/$(date +%Y%m%d-%H%M%S)-$RUN_NAME.log"
exec > >(tee -a "$LOG") 2>&1

echo "pipeline: run=$RUN_NAME bins=$BINS days=$DAYS seed=$SEED small_run=$SMALL_RUN"
echo "pipeline: steps=$STEPS threads=${OMP_NUM_THREADS:-all} log=$LOG"

step() {  # step <label> <command...>
  local label="$1" t0=$SECONDS
  shift
  echo "=== [$(date +%T)] $label"
  "$@"
  echo "=== [$(date +%T)] $label done in $((SECONDS - t0)) s"
}

keep_stdout() {  # keep_stdout <file> <command...>: stdout goes to <file> and to the log
  local out="$1"
  shift
  "$@" | tee "$out"
}

with_small_run() { [[ "$SMALL_RUN" == 1 && "$RUN_NAME" != "$SMALL_NAME" ]]; }

simulate() {  # simulate <run> <bins>
  step "sim $1" "$PY" -m compactor_sim --config config.yaml \
    --bins "$2" --days "$DAYS" --seed "$SEED" --out "runs/$1"
}

train() {  # train <run>
  step "train $1" "$PY" -m weight_train train --data "runs/$1" --out "models/$1" --seed "$SEED"
}

for s in $STEPS; do
  case "$s" in
    sim)
      simulate "$RUN_NAME" "$BINS"
      if with_small_run; then simulate "$SMALL_NAME" "$SMALL_BINS"; fi
      ;;
    validate)
      step validate keep_stdout "runs/$RUN_NAME/validate_report.txt" "$PY" validate.py "runs/$RUN_NAME"
      ;;
    baseline)
      step baseline keep_stdout "runs/$RUN_NAME/baseline_report.txt" "$PY" baseline.py "runs/$RUN_NAME"
      ;;
    train)
      if with_small_run; then train "$SMALL_NAME"; fi
      train "$RUN_NAME"
      ;;
    predict)
      step predict "$PY" -m weight_train predict --models "models/$RUN_NAME" \
        --input "runs/$RUN_NAME/hourly.parquet" --output "models/$RUN_NAME/predictions.parquet"
      ;;
    report)
      step report "$PY" -m weight_train report --models "models/$RUN_NAME"
      ;;
    site)
      step site "$PY" make_site.py
      ;;
  esac
done

echo "pipeline: finished. Outputs in runs/$RUN_NAME and models/$RUN_NAME, log $LOG"
if [[ "$RUN_NAME" != full400 ]]; then
  echo "pipeline: note: the results site shows runs/full400, models/full400 and models/bins25 only"
fi
