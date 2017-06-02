# Production Deployment

1. Install `docker` and other tools that are part of @davidneudorfer's standard
  provisioning process.
2. Create `/mnt-overpass` and `/mnt-storage` (on additional disks, if needed,
  auto-mounting on boot)
3. Copy `systemd/*` to `/etc/systemd/system/`.
4. Create `/etc/exports.env` with production environment variables.
5. Reload the systemd units: `systemctl daemon-reload`
6. Enable each of the units copied from `systemd`: `systemctl enable <unit
  file>`
7. Bootstrap `/mnt-overpass` with metadata
8. Start everything: `systemctl start osm-export-tool.target`

N.b: step #8 may need to be done twice, as the migration step (part of
`docker.django.service`) doesn't wait for PostgreSQL to be fully online before
failing (which takes longer on first-run while the Postgres database is
initialized).

To upgrade, `systemctl restart osm-export-tool.target` should work, pulling down
new versions of Docker images.
