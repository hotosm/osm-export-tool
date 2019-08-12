import argparse
import json
import os
import logging
import subprocess
from osmium.replication import server
from datetime import datetime,timezone


parser = argparse.ArgumentParser(description='osmium-tool based pipeline')
parser.add_argument('directory', help='Working directory - needs a lot of space')
parsed = parser.parse_args()
workdir = parsed.directory
planet = os.path.join(workdir,'planet.osm.pbf')

PLANET_OSM_PBF = 'https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf'

if not os.path.isfile(planet):
	logging.warning('Downloading planet.osm.pbf')
	subprocess.call(['wget','-O',planet,PLANET_OSM_PBF])

fileinfo = json.loads(subprocess.check_output(['osmium','fileinfo','-j',planet]))
timestamp = fileinfo['header']['option']['osmosis_replication_timestamp']
timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
timestamp = timestamp.replace(tzinfo=timezone.utc)
logging.warning("Timestamp is {0}".format(timestamp))

daily = server.ReplicationServer('https://planet.openstreetmap.org/replication/day/')
seqnum = daily.timestamp_to_sequence(timestamp)
logging.warning("Seqnum is {0}".format(seqnum))
retval = daily.apply_diffs_to_file(planet,os.path.join(workdir,'planet-new.osm.pbf'),seqnum)

print(retval)
