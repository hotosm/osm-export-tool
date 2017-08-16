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
9. Migrate the database: `systemctl start docker.django-migration`
10. Restart everything to ensure that migrations are picked up: `systemctl restart osm-export-tool.target`

N.b: step #9 may need to be done twice, as the migration step doesn't wait for PostgreSQL to be
fully online before failing (which takes longer on first-run while the Postgres database is
initialized). To determine whether it applied migrations successfully, run `journalctl -u
docker.django-migration`

To upgrade, run `docker pull` for each image that needs to be upgraded and then run `systemctl
restart osm-export-tool.target` to restart.

If the only thing that has changed is application code, the quick version is: `docker pull quay.io/hotosm/osm-export-tool2 && systemctl restart docker.django.service`. This will restart only the services with dependencies on changed application code (`celery`, `celery-beat`, `django`, and `nginx` (for static assets)).

Unused / unlinked Docker images should be cleaned up periodically to avoid running out of disk space: `docker image prune -a`

## Logs

Systemd's `journalctl` should be used to view logs. To tail celery logs, run: `journalctl -fu
docker.celery`.

## Backups

`docker.postgresql-backup.{service,timer}` define a unit that runs daily to back the database up to
S3. To check its schedule, run `systemctl list-timers`.

## SSL Certificates

`docker.nginx-ssl.{service,timer}` define a unit that runs monthly to register
SSL certificates using [Let's Encrypt](https://letsencrypt.org/). To check its
schedule, run `systemctl list-timers`.
