#!/usr/bin/env bash
# Start one pipeline run as an OpenShift Job. Settings come from env vars
# (names and defaults: pipeline-job.yaml). Examples:
#   deploy/openshift/run-pipeline.sh --follow                                    # full run, 400 machines
#   STEPS="train predict report site" deploy/openshift/run-pipeline.sh           # retrain on existing data
#   RUN_NAME=bins100 BINS=100 SMALL_RUN=0 CPU=2 CPU_REQUEST=1 MEMORY=4Gi MEMORY_REQUEST=2Gi \
#     deploy/openshift/run-pipeline.sh                                           # small project quota
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PARAMS=(RUN_NAME BINS DAYS SEED SMALL_RUN STEPS CPU CPU_REQUEST MEMORY MEMORY_REQUEST)

command -v oc >/dev/null || { echo "oc CLI not found: see deploy/openshift/README.md" >&2; exit 1; }
oc whoami >/dev/null 2>&1 || { echo "Not logged in to OpenShift: run 'oc login ...' first" >&2; exit 1; }

args=()
for p in "${PARAMS[@]}"; do
  if [[ -n "${!p:-}" ]]; then args+=(-p "$p=${!p}"); fi
done

job="$(oc process --local -f "$HERE/pipeline-job.yaml" "${args[@]}" | oc create -f - -o name)"
name="${job#*/}"
echo "Started $job in project $(oc project -q)"
echo "  logs:     oc logs -f $job"
echo "  status:   oc get $job"
echo "  results:  oc rsync \$(oc get pod -l app.kubernetes.io/name=compactor-site -o jsonpath='{.items[0].metadata.name}'):/data/models ./openshift-results"

if [[ "${1:-}" == "--follow" ]]; then
  echo "Waiting for the pod to start..."
  oc wait --for=condition=Ready pod -l "job-name=$name" --timeout=15m
  oc logs -f "$job"
fi
