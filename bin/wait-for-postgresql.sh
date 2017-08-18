#!/usr/bin/env bash

set -eo pipefail

until psql "${DATABASE_URL/postgis:\/\//postgres:\/\/}" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

exec $*
