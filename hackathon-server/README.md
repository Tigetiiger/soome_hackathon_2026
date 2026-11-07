# hackathon-server (auto-synced mirror)

Code and docs from `/home/hackathon` on the `hackathon` server, pushed every
5 minutes by `/home/hackathon/.code-sync/sync.sh` (systemd user timer `code-sync.timer`).

Do not edit files here by hand: this folder is rebuilt from the server on every
sync, so manual changes are overwritten. Virtualenvs, node_modules, data/ folders,
model binaries, images, logs and files over 1024 KB are excluded.
