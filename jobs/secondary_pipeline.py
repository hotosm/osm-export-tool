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

option = fileinfo['header']['option']

if 'osmosis_replication_sequence_number' in option:
	seqnum = option['osmosis_replication_sequence_number']
else:
	timestamp = fileinfo['header']['option']['osmosis_replication_timestamp']
	timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
	timestamp = timestamp.replace(tzinfo=timezone.utc)
	logging.warning("Timestamp is {0}".format(timestamp))
	daily = server.ReplicationServer('https://planet.openstreetmap.org/replication/day')
	seqnum = daily.timestamp_to_sequence(timestamp)

logging.warning("Seqnum is {0}".format(seqnum))

latest = daily.get_state_info().sequence

try:
	os.mkdir(os.path.join(workdir,'tmp'))
except:
	pass

for i in range(seqnum+1,latest):
	subprocess.call(['wget','-O',os.path.join(workdir,'tmp','{0}.osc.gz'.format(i)),daily.get_diff_url(i)])

g = glob.glob(os.path.join(workdir,'tmp','*.osc.gz'))
subprocess.call(['osmium','merge-changes','--overwrite','--simplify',*g,'-o',os.path.join(workdir,'merged-changes.osc.gz')])
subprocess.call(['osmium','apply-changes','--output-header',"'osmosis_replication_sequence_number={0}'".format(latest),planet,os.path.join(workdir,'merged-changes.osc.gz','-o',os.path.join(workdir,'planet-updated.osm.pbf'))])

# move the old one into the new one
# remove the tmp directory
