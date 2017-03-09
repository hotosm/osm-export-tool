import json
import sqlite3

from utils import overpass, osmconf, pbf, osmparse, thematic_shp
from shapely.geometry import asShape
from jobs.presets import PresetParser
from utilities import categorised_tags, _tag_dict, _filters

import os
import json
import subprocess
import glob
import zipfile

job_name = 'SLE'
extent_path = 'hdx/adm0/SLE_adm0.geojson'

stage_dir = 'stage/' + job_name + "/"
f = open(extent_path)

features = json.loads(f.read())['features']
assert len(features) == 1
shape = asShape(features[0]['geometry'])
bounds = shape.bounds
bbox = "{0},{1},{2},{3}".format(bounds[1],bounds[0],bounds[3],bounds[2])
url = "http://overpass-api.de/api/interpreter"

parser = PresetParser(preset='./hdx/hdx_presets.xml')
tags_dict = parser.parse()
categories = categorised_tags(tags_dict)
o = overpass.Overpass(url,bbox,stage_dir,job_name,[],debug=True)
o.run_query()
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

res = cur.execute('create table buildings_polygons as select Geometry, osm_id, name, building,building_levels,building_materials,addr_housenumber,addr_street,addr_city,office from planet_osm_polygon where building is not null and ST_Intersects(GeomFromText(?),Geometry)',(shape.wkt,))
res = cur.execute('create table roads_lines as select Geometry, osm_id, name, highway,surface,smoothness,width,lanes,oneway,bridge,layer from planet_osm_line where highway is not null and ST_Intersects(GeomFromText(?),Geometry)',(shape.wkt,))
res = cur.execute('create table roads_polygons as select Geometry, osm_id, name, highway,surface,smoothness,width,lanes,oneway,bridge,layer from planet_osm_polygon where highway is not null and ST_Intersects(GeomFromText(?),Geometry)',(shape.wkt,))
res = cur.execute("create table waterways_lines as select Geometry, osm_id, name, waterway, covered,width,depth,layer,blockage,tunnel,natural,water from planet_osm_line where (waterway is not null OR water is not null OR natural IN ('water', 'wetland', 'coastline', 'bay')) and ST_Intersects(GeomFromText(?),Geometry)",(shape.wkt,))
res = cur.execute("create table waterways_polygons as select Geometry, osm_id, name, waterway, covered,width,depth,layer,blockage,tunnel,natural,water from planet_osm_polygon  where (waterway is not null OR water is not null OR natural IN ('water', 'wetland', 'coastline', 'bay'))  and ST_Intersects(GeomFromText(?),Geometry)",(shape.wkt,))
res = cur.execute('create table points_of_interest_points as select Geometry, osm_id, name, amenity, man_made, shop, tourism, opening_hours, beds, rooms, addr_housenumber, addr_street, addr_city from planet_osm_point where (amenity is not null OR man_made is not null OR shop is not null OR tourism is not null) and ST_Intersects(GeomFromText(?),Geometry)',(shape.wkt,))
res = cur.execute('create table points_of_interest_polygons as select Geometry, osm_id, name, amenity, man_made, shop, tourism, opening_hours, beds, rooms, addr_housenumber, addr_street, addr_city from planet_osm_polygon where (amenity is not null OR man_made is not null OR shop is not null OR tourism is not null) and ST_Intersects(GeomFromText(?),Geometry)',(shape.wkt,))
res = cur.execute("create table admin_boundaries_points as select Geometry, osm_id, name, boundary, admin_level, place from planet_osm_point where boundary = 'administrative' OR admin_level IS NOT NULL and ST_Intersects(GeomFromText(?),Geometry)",(shape.wkt,))
res = cur.execute("create table admin_boundaries_lines as select Geometry, osm_id, name, boundary, admin_level, place from planet_osm_line where boundary = 'administrative' OR admin_level IS NOT NULL and ST_Intersects(GeomFromText(?),Geometry)",(shape.wkt,))
res = cur.execute("create table admin_boundaries_polygons as select Geometry, osm_id, name, boundary, admin_level, place from planet_osm_polygon where boundary = 'administrative' OR admin_level IS NOT NULL and ST_Intersects(GeomFromText(?),Geometry)",(shape.wkt,))

tables = [
    ('buildings_polygons','MULTIPOLYGON'),
    ('roads_lines','LINESTRING'),
    ('roads_polygons','MULTIPOLYGON'),
    ('waterways_lines','LINESTRING'),
    ('waterways_polygons','MULTIPOLYGON'),
    ('points_of_interest_points','POINT'),
    ('points_of_interest_polygons','MULTIPOLYGON'),
    ('admin_boundaries_points','POINT'),
    ('admin_boundaries_lines','LINESTRING'),
    ('admin_boundaries_polygons','MULTIPOLYGON')
]

for table in tables:
    cur.execute("SELECT RecoverGeometryColumn(?, 'GEOMETRY', 4326, ?, 'XY')",(table[0],table[1]))
    conn.commit()
    subprocess.check_call('ogr2ogr -f "ESRI Shapefile" {1}{0}.shp {2} -lco ENCODING=UTF-8 -sql "select * from {0};"'.format(table[0],stage_dir,s),shell=True,executable='/bin/bash')
    with zipfile.ZipFile(stage_dir + table[0] + ".zip",'w',zipfile.ZIP_DEFLATED) as z:
        z.write(stage_dir + table[0] + ".shp",table[0] + ".shp")
        z.write(stage_dir + table[0] + ".dbf",table[0] + ".dbf")
        z.write(stage_dir + table[0] + ".prj",table[0] + ".prj")
        z.write(stage_dir + table[0] + ".shx",table[0] + ".shx")
        z.write(stage_dir + table[0] + ".cpg",table[0] + ".cpg")

conn.close()
