#!/usr/bin/env bash
# Start one pipeline run as an OpenShift Job. Settings come from env vars
# (names and defaults: pipeline-job.yaml). Examples:
#   deploy/openshift/run-pipeline.sh --follow                                    # full run, 400 machines
#   STEPS="train predict report site" deploy/openshift/run-pipeline.sh           # retrain on existing data
#   RUN_NAME=bins100 BINS=100 SMALL_RUN=0 CPU=2 CPU_REQUEST=1 MEMORY=4Gi MEMORY_REQUEST=2Gi \
#     deploy/openshift/run-pipeline.sh                                           # small project quota
# With --follow it streams the log and exits non-zero if the run failed.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PARAMS=(RUN_NAME BINS DAYS SEED SMALL_RUN STEPS CPU CPU_REQUEST MEMORY MEMORY_REQUEST)
STATUS_TRIES=12   # x 5 s: the Job status can lag the end of the log

command -v oc >/dev/null || { echo "oc CLI not found: see deploy/openshift/README.md" >&2; exit 1; }
oc whoami >/dev/null 2>&1 || { echo "Not logged in to OpenShift: run 'oc login ...' first" >&2; exit 1; }
oc get deploy/compactor-site >/dev/null 2>&1 \
  || { echo "No compactor-site in project $(oc project -q): run deploy/openshift/deploy.sh first" >&2; exit 1; }

# The Job is pinned to the site pod's node (ReadWriteOnce volume), so the site pod must be up.
if [[ -z "$(oc get deploy/compactor-site -o jsonpath='{.status.readyReplicas}')" ]]; then
  echo "Starting the site pod first (the Job runs next to it, where the data volume is mounted)..."
  oc scale deploy/compactor-site --replicas=1
  oc rollout status deploy/compactor-site --timeout=5m
fi

args=()
for p in "${PARAMS[@]}"; do
  if [[ -n "${!p:-}" ]]; then args+=(-p "$p=${!p}"); fi
done

job="$(oc process --local -f "$HERE/pipeline-job.yaml" ${args[@]+"${args[@]}"} | oc create -f - -o name)"
echo "Started $job in project $(oc project -q)"
echo "  logs:     oc logs -f $job"
echo "  status:   oc get $job"
echo "  results:  oc rsync \$(oc get pod -l app.kubernetes.io/name=compactor-site -o jsonpath='{.items[0].metadata.name}'):/data/models ./openshift-results"

[[ "${1:-}" == "--follow" ]] || exit 0

oc logs -f --pod-running-timeout=15m "$job"
for _ in $(seq "$STATUS_TRIES"); do
  if [[ "$(oc get "$job" -o jsonpath='{.status.succeeded}')" == 1 ]]; then
    echo "Run succeeded."
    exit 0
  fi
  if [[ -n "$(oc get "$job" -o jsonpath='{.status.failed}')" ]]; then
    echo "Run FAILED: see the log above, or: oc describe $job" >&2
    exit 1
  fi
  sleep 5
done
echo "The log ended but the Job has not finished: check oc get $job" >&2
exit 1
