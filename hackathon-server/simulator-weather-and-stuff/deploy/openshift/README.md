# Running the compactor pipeline on Red Hat OpenShift

The image is built **inside the cluster**, so you need no docker or podman locally.
Each computation is a Kubernetes **Job** that runs
`sim → validate → baseline → train → predict → report → site` and writes to a persistent
volume. A small web pod serves the results site from that volume at an HTTPS Route.

| file | role |
|---|---|
| `Containerfile` | image: UBI 9 + Python 3.12, package versions pinned to the local `.venv` (`constraints.txt`) |
| `base.yaml` | volume `compactor-data` (5 Gi), image stream and build config `compactor-sim` |
| `site.yaml` | results website: Deployment, Service, Route `compactor-site` |
| `pipeline-job.yaml` | Job template, one pipeline run (parameters: run size, steps, CPU and memory) |
| `pipeline.sh` | what the Job runs. Also runnable locally |
| `deploy.sh` | set up, or rebuild the image after code changes |
| `run-pipeline.sh` | start a run |

## 1. Install the `oc` CLI

Either download it from the web console (**?** → *Command Line Tools*), or:

```bash
curl -fsSL https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz \
  | tar -xz -C ~/.local/bin oc
oc version --client
```

## 2. Log in and choose a project

In the web console click your name (top right) → *Copy login command* → *Display token*, then:

```bash
oc login --token=sha256~XXXX --server=https://api.<cluster-domain>:6443
oc new-project compactor-sim      # Developer Sandbox: skip this and use your existing <user>-dev project
```

## 3. Set up (once, and again after code changes)

```bash
deploy/openshift/deploy.sh
```

This creates the volume and build, uploads the code (~0.1 MB, without `runs/`, `models/` or `.venv`),
builds the image (a few minutes the first time), starts the site and prints its URL.

## 4. Compute

```bash
deploy/openshift/run-pipeline.sh --follow        # full: 400 machines x 365 days, plus the 25-machine run
```

`--follow` streams the log and exits non-zero if the run failed (Ctrl+C stops only the log, not the Job).
If the site pod is not running (for example scaled down), `run-pipeline.sh` starts it first.

By default the Job requests 4 CPU / 6 GiB and may use up to 8 CPU / 10 GiB. 400-machine training peaks
around 3 GiB. LightGBM runs one thread per CPU of the limit. Training is CPU-bound; at 8 cores expect
somewhere around 30–60 minutes for the full run (not yet measured on a cluster). The finished Job is
kept for 7 days.

Any template parameter can be set as an env var:

```bash
# retrain on data already on the volume (skips the simulation)
STEPS="train predict report site" deploy/openshift/run-pipeline.sh

# more cores, if your quota allows
CPU=16 CPU_REQUEST=8 deploy/openshift/run-pipeline.sh

# small project quota (e.g. Developer Sandbox)
RUN_NAME=bins100 BINS=100 SMALL_RUN=0 CPU=2 CPU_REQUEST=1 MEMORY=4Gi MEMORY_REQUEST=2Gi \
  deploy/openshift/run-pipeline.sh
```

Parameters: `RUN_NAME BINS DAYS SEED SMALL_RUN STEPS CPU CPU_REQUEST MEMORY MEMORY_REQUEST`
(defaults are in `pipeline-job.yaml`). The site shows `full400` and `bins25` only. Any other
`RUN_NAME` still gets its own `models/<run>/REPORT.md`.

## 5. Results

```bash
oc get route compactor-site                       # site URL
oc get jobs -l app.kubernetes.io/name=compactor-pipeline
oc logs -f job/<job-name>                          # also saved in /data/logs on the volume

SITE_POD=$(oc get pod -l app.kubernetes.io/name=compactor-site -o jsonpath='{.items[0].metadata.name}')
oc rsync $SITE_POD:/data/models ./openshift-results      # copy models + REPORT.md + plots back
oc rsync runs/full400 $SITE_POD:/data/runs/              # or upload local data, then STEPS="train ..."
```

## Notes

* **Cluster requirements.** The internal image registry must be enabled, you must be allowed
  Docker-strategy builds (check with `oc auth can-i create builds/docker`), and builds need internet
  access to PyPI and the Red Hat UBI repos. If any of these is missing, `deploy.sh` fails at the build step.
* **Single-node volume.** The volume is ReadWriteOnce, so Job pods are pinned to the node where the site
  pod runs. Keep `compactor-site` running. If a Job pod stays `Pending`, check `oc describe pod -l job-name=<job>`.
  The usual cause is project CPU/memory quota, so lower `CPU`/`MEMORY`.
* **Public URL.** The Route is reachable from the internet (all data is synthetic). To keep it private, run
  `oc delete route compactor-site` and `oc port-forward svc/compactor-site 8080`, then open http://localhost:8080.
* **Clean up.** `oc delete all,pvc,bc,is,route -l app.kubernetes.io/part-of=compactor-sim` (this also deletes the data).
* **Test locally.** `pipeline.sh` runs outside the cluster too. Set `DATA_DIR`, `PYTHON`, and symlink
  `runs/ models/ site/` into `DATA_DIR` the same way the Containerfile does.
