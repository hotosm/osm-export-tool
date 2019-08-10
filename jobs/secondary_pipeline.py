import argparse
import json
import os
import logging
import subprocess

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
print(['header']['options'])
timestamp = fileinfo['header']['option']['osmosis_replication_timestamp']
