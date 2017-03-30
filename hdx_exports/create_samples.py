import sqlite3

from utils import overpass, osmconf, pbf, osmparse, thematic_shp
from feature_selection import FeatureSelection
from hdx_export_set import HDXExportSet

f_s = FeatureSelection(open('hdx/example_preset.yml').read())
extent_path = 'hdx/adm0/SEN_adm0.geojson'
h = HDXExportSet(extent_path,f_s,'hotosm_senegal')

bounds = h.bounds
bbox = "{0},{1},{2},{3}".format(bounds[1],bounds[0],bounds[3],bounds[2])
url = "http://overpass-api.de/api/interpreter"

stage_dir = '../stage/' + h.base_slug + "/"
categories = {'points':f_s.key_union,'lines':f_s.key_union,'polygons':f_s.key_union}
o = overpass.Overpass(bbox,stage_dir,h.base_slug,filters=[],debug=True)
#o.run_query()
o.filter()

conf = osmconf.OSMConfig(categories=categories,job_name=h.base_slug)
conf.create_osm_conf(stage_dir=stage_dir)
o2p = pbf.OSMToPBF(osm=stage_dir+h.base_slug+".osm",pbffile=stage_dir+h.base_slug+".pbf")
o2p.convert()
o = osmparse.OSMParser(osm=stage_dir+h.base_slug+".pbf",sqlite=stage_dir+h.base_slug+".sqlite",osmconf=stage_dir+h.base_slug+".ini",debug=True)
o.create_spatialite()
o.create_default_schema()

sqlite = stage_dir + h.base_slug + ".sqlite"
conn = sqlite3.connect(sqlite)
conn.enable_load_extension(True)
cur = conn.cursor()
cur.execute("select load_extension('mod_spatialite')")
create_sqls, index_sqls = f_s.sqls
for query in create_sqls:
    cur.execute(query,(h.clipping_polygon.wkt,))

for query in index_sqls:
    cur.execute(query)
conn.commit()
conn.close()
