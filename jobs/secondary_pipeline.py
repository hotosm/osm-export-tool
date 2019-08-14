import argparse
import glob
import shutil
import json
import os
import logging
import subprocess
from osmium.replication import server
from datetime import datetime,timezone

# 0 3 * * * /home/exports/venv/bin/python /home/exports/osm-export-tool/jobs/secondary_pipeline.py /mnt/data/planet/ >> /home/exports/secondary_pipeline.log 2>&1

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
daily = server.ReplicationServer('https://planet.openstreetmap.org/replication/day')

if 'osmosis_replication_sequence_number' in option:
	seqnum = int(option['osmosis_replication_sequence_number'])
else:
	timestamp = fileinfo['header']['option']['osmosis_replication_timestamp']
	timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
	timestamp = timestamp.replace(tzinfo=timezone.utc)
	logging.warning("Timestamp is {0}".format(timestamp))
	seqnum = daily.timestamp_to_sequence(timestamp)

logging.warning("Seqnum is {0}".format(seqnum))
latest = daily.get_state_info().sequence
logging.warning("Latest is {0}".format(latest))
if seqnum == latest:
	exit(0)

try:
	os.mkdir(os.path.join(workdir,'tmp'))
except:
	pass

try:
	for i in range(seqnum+1,latest+1):
		subprocess.call(['wget','-O',os.path.join(workdir,'tmp','{0}.osc.gz'.format(i)),daily.get_diff_url(i)])

	g = glob.glob(os.path.join(workdir,'tmp','*.osc.gz'))
	subprocess.call(['osmium','merge-changes','--overwrite','--simplify',*g,'-o',os.path.join(workdir,'merged-changes.osc.gz')])
	subprocess.call(['osmium','apply-changes','--output-header','osmosis_replication_sequence_number={0}'.format(latest),planet,os.path.join(workdir,'merged-changes.osc.gz'),'-o',os.path.join(workdir,'planet-updated.osm.pbf')])
	os.rename(os.path.join(workdir,'planet-updated.osm.pbf'),planet)
except:
	pass
finally:
	shutil.rmtree(os.path.join(workdir,'tmp'))

