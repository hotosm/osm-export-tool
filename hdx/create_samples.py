import json
import sqlite3

from utils import overpass, osmconf, pbf, osmparse, thematic_shp
from shapely.geometry import asShape

import os
import json
import subprocess
import glob
import zipfile

from feature_selection import FeatureSelection

f_s = FeatureSelection(open('hdx/example_preset.yml').read())

job_name = 'SLE'
extent_path = 'hdx/adm0/SLE_adm0.geojson'
f = open(extent_path)

features = json.loads(f.read())['features']
assert len(features) == 1
shape = asShape(features[0]['geometry'])
bounds = shape.bounds
bbox = "{0},{1},{2},{3}".format(bounds[1],bounds[0],bounds[3],bounds[2])
url = "http://overpass-api.de/api/interpreter"

stage_dir = '../stage/' + job_name + "/"
categories = {'points':f_s.key_union,'lines':f_s.key_union,'polygons':f_s.key_union}
o = overpass.Overpass(url,bbox,stage_dir,job_name,[],debug=True)
#o.run_query()
o.filter()

conf = osmconf.OSMConfig(categories=categories,job_name=job_name)
conf.create_osm_conf(stage_dir=stage_dir)
o2p = pbf.OSMToPBF(osm=stage_dir+job_name+".osm",pbffile=stage_dir+job_name+".pbf")
o2p.convert()
o = osmparse.OSMParser(osm=stage_dir+job_name+".pbf",sqlite=stage_dir+job_name+".sqlite",osmconf=stage_dir+job_name+".ini",debug=True)
o.create_spatialite()
o.create_default_schema()

s = stage_dir + job_name + ".sqlite"

conn = sqlite3.connect(s)
conn.enable_load_extension(True)
cur = conn.cursor()
cur.execute("select load_extension('mod_spatialite')")
create_sqls, index_sqls = f_s.sqls
for query in create_sqls:
    cur.execute(query,(shape.wkt,))

for query in index_sqls:
    cur.execute(query)
conn.commit()
conn.close()

print "TABLES"
print f_s.tables

for table in f_s.tables:
    subprocess.check_call('ogr2ogr -f "ESRI Shapefile" {1}{0}.shp {2} -lco ENCODING=UTF-8 -sql "select * from {0};"'.format(table,stage_dir,s),shell=True,executable='/bin/bash')
    with zipfile.ZipFile(stage_dir + table + ".zip",'w',zipfile.ZIP_DEFLATED) as z:
        z.write(stage_dir + table + ".shp",table + ".shp")
        z.write(stage_dir + table + ".dbf",table + ".dbf")
        z.write(stage_dir + table + ".prj",table + ".prj")
        z.write(stage_dir + table + ".shx",table + ".shx")
        z.write(stage_dir + table + ".cpg",table + ".cpg")
