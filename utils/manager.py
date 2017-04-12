from django.contrib.gis.geos import GEOSGeometry, Polygon
from osm_xml import OSM_XML
from osm_pbf import OSM_PBF
from kml import KML
from geopackage import Geopackage
from shp import Shapefile
from theme_gpkg import ThematicGPKG
from theme_shp import ThematicSHP
from feature_selection.feature_selection import FeatureSelection
import logging
import os
import json

y = '''
buildings:
  types:
    - polygons
  select:
    - name
    - building
    - building_levels
    - building_materials
    - addr_housenumber
    - addr_street
    - addr_city
    - office
  where: building IS NOT NULL

roads:
  types:
    - lines
    - polygons
  select:
    - name
    - highway
    - surface
    - smoothness
    - width
    - lanes
    - oneway
    - bridge
    - layer
  where: highway IS NOT NULL
 
waterways:
  types: 
    - lines
    - polygons
  select:
    - name
    - waterway
    - covered
    - width
    - depth
    - layer
    - blockage
    - tunnel
    - natural
    - water
  where: waterway IS NOT NULL OR water IS NOT NULL OR natural IN ('water','wetland','coastline','bay')

points_of_interest:
  types: 
    - points
    - polygons
  select:
    - name
    - amenity
    - man_made
    - shop
    - tourism
    - opening_hours
    - beds
    - rooms
    - addr_housenumber
    - addr_street
    - addr_city
  where: amenity IS NOT NULL OR man_made IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL

admin_boundaries:
  types: 
    - points
    - lines
    - polygons
  select:
    - name
    - boundary
    - admin_level
    - place
  where: boundary = 'administrative' OR admin_level IS NOT NULL
'''

logging.basicConfig(level=logging.DEBUG)

stage_dir = 'scratch/'
try:
    os.makedirs('scratch', 6600)
except:
    print "Exists"
feature_selection = FeatureSelection(y)
#aoi_geom = GEOSGeometry(open('../hdx_exports/adm0/SEN_adm0.geojson').read())
#aoi_geom = Polygon.from_bbox((-10.80029,6.3254236,-10.79809,6.32752))
aoi_geom = GEOSGeometry('POLYGON((-17.4682611807514 14.7168486569183,-17.4682611807514 14.6916060414416,-17.4359733230442 14.6916060414416,-17.4359733230442 14.7168486569183,-17.4682611807514 14.7168486569183))')

#aoi_geom = aoi_geom.buffer(0.02)
#aoi_geom = aoi_geom.simplify(0.01)
osm_xml = OSM_XML(aoi_geom, stage_dir + 'osm_xml.osm')
osm_xml.run()
osm_pbf = OSM_PBF(stage_dir+'osm_xml.osm',stage_dir+'osm_pbf.pbf')
osm_pbf.run()
geopackage = Geopackage(stage_dir+'osm_pbf.pbf',stage_dir+'geopackage.gpkg',stage_dir+'osmconf.ini',feature_selection,aoi_geom)
geopackage.run()
#kml = KML(stage_dir + 'geopackage.gpkg',stage_dir + 'kml.kmz')
#kml.run()
#shp = Shapefile(stage_dir + 'geopackage.gpkg',stage_dir + 'shapefile.shp.zip')
#shp.run()
theme_gpkg = ThematicGPKG(stage_dir+'geopackage.gpkg',feature_selection,stage_dir,per_theme=True)
#theme_gpkg.run()
theme_gpkg.run2()
#theme_shp = ThematicSHP(stage_dir+'geopackage.gpkg',stage_dir+'thematic_shps',feature_selection,aoi_geom,per_theme=True)
#theme_shp.run()

