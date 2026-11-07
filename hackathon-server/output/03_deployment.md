# Deployment — europress.acq.ee

DNS: `A europress.acq.ee → 194.204.20.82` (this machine).

## Components

| Piece | Where | Runs as |
|---|---|---|
| Data pipeline | `europress-dashboard/pipeline/build_data.py` → `public/data/*.json`, `ai-workspace/data/*` | manual |
| Web + AI server | `europress-dashboard/server/server.mjs` (Node, no deps) on `127.0.0.1:8080` | `systemctl --user europress-dashboard` |
| HTTPS proxy | `europress-dashboard/bin/caddy` (v2.8.4, checksum verified) + `Caddyfile`, auto Let's Encrypt | `systemctl --user europress-caddy` |
| AI | `claude -p` (Claude Code CLI, existing login), read-only in `ai-workspace/` | spawned per question |

## One-time root step (needed because ports 80/443 are privileged)

```bash
sudo setcap cap_net_bind_service=+ep /home/hackathon/europress-dashboard/bin/caddy
sudo loginctl enable-linger hackathon      # keep user services running after logout / reboot
```

Then:

```bash
systemctl --user enable --now europress-caddy
curl -I https://europress.acq.ee
```

Ports 80 and 443 must be open in any cloud firewall in front of the machine.

## Operations

```bash
# rebuild data after changing the pipeline
~/soome_hackathon_2026/.venv/bin/python -I ~/europress-dashboard/pipeline/build_data.py
# restart / logs
systemctl --user restart europress-dashboard
tail -f ~/europress-dashboard/logs/server.log      # JSON lines, one per AI question
tail -f ~/europress-dashboard/logs/access.log      # Caddy
```

Environment (in the unit file): `PORT=8080 HOST=127.0.0.1 AI_MODEL=sonnet`.

## Current state (2026-11-07): tailnet only

- Public 80/443 are **not reachable**: the machine is `10.10.10.40` behind a NAT that owns `194.204.20.82`, and the router does not forward ports. Let's Encrypt timed out, so Caddy is installed but **disabled** (`systemctl --user disable europress-caddy`).
- The dashboard listens on `127.0.0.1:8080` and the Tailscale IP `100.87.158.27:8080` (`HOST=127.0.0.1,100.87.158.27` in the unit). Not on `eth0`.
- Open from any device on the tailnet: **http://hackathon.tail8f13e3.ts.net:8080** (or http://100.87.158.27:8080).
- Linger is enabled, so the service survives logout and reboot.

### To publish on europress.acq.ee later
1. Ask whoever runs `194.204.20.82` to forward TCP 80 and 443 to `10.10.10.40`, **or** put a small public VPS in front (Caddy there, proxying over Tailscale to `100.87.158.27:8080`, and the Zone.ee A record pointed at the VPS).
2. For port forwarding: `systemctl --user enable --now europress-caddy`. Caddy gets the certificate automatically.
