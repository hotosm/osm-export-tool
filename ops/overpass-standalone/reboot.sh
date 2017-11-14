#!/usr/bin/env bash

EXEC_DIR="/srv/osm3s/bin"
DB_DIR="/mnt"

if [[ -z $DB_DIR || -z $EXEC_DIR ]]; then
  echo "To use this script, you must do the following things:"
  echo "- edit the definitions of DB_DIR and EXEC_DIR in this file according to your local settings"
  echo "- put this file into your crontab, with time spec @reboot"
  exit 0
fi

# another lock file exists at /dev/shm/
rm -f "$DB_DIR/osm3s_v0.7.54_osm_base"
nohup "$EXEC_DIR/dispatcher" --osm-base --attic --rate-limit=5 --space=10737418240 "--db-dir=$DB_DIR" >>"$EXEC_DIR/osm_base.out" &

if [[ -s "$DB_DIR/replicate_id" ]]; then
  sleep 20
  nohup "$EXEC_DIR/fetch_osc_and_apply.sh" "http://planet.osm.org/replication/minute" --meta=attic >> "$EXEC_DIR/fetch_osc_and_apply.out" &

# add this to crontab: see https://dev.overpass-api.de/blog/systemd.html
