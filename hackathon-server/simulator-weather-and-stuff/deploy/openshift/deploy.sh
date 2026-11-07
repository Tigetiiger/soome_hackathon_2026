#!/usr/bin/env bash
# Set up the compactor pipeline in the current OpenShift project: storage, image build
# (in-cluster, no local docker/podman needed) and the results site.
# Re-run after code changes to rebuild the image. Then start a run with run-pipeline.sh.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
# Uploaded into the image: code only. runs/, models/ and .venv stay local.
REQUIRED=(compactor_sim weight_train tests deploy/openshift config.yaml requirements.txt pytest.ini
          make_site.py validate.py baseline.py)
OPTIONAL=(README.md AI_WORK_SUMMARY.md)   # make_site.py links to these when present

command -v oc >/dev/null || { echo "oc CLI not found: see deploy/openshift/README.md" >&2; exit 1; }
oc whoami >/dev/null 2>&1 || { echo "Not logged in to OpenShift: run 'oc login ...' first" >&2; exit 1; }
echo "OpenShift project: $(oc project -q)"

oc apply -f "$HERE/base.yaml"

sources=("${REQUIRED[@]}")
for f in "${OPTIONAL[@]}"; do
  if [[ -e "$ROOT/$f" ]]; then sources+=("$f"); fi
done
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
tar -C "$ROOT" --exclude='__pycache__' -czf "$tmp/src.tar.gz" "${sources[@]}"
echo "Uploading $(du -h "$tmp/src.tar.gz" | cut -f1) of source and building the image..."
oc start-build compactor-sim --from-archive="$tmp/src.tar.gz" --follow --wait

# The site goes up after the first build so its pod finds the image.
oc apply -f "$HERE/site.yaml"
oc rollout status deploy/compactor-site --timeout=5m

echo
echo "Results site: https://$(oc get route compactor-site -o jsonpath='{.spec.host}')"
echo "Start a run:  $HERE/run-pipeline.sh --follow"
