from osm_xml import OSM_XML
from osm_pbf import OSM_PBF
from geopackage import Geopackage
from shp import Shapefile
from theme_gpkg import ThematicGPKG
from theme_shp import ThematicSHP
from kml import KML

FORMAT_NAMES = {}
for cls in [OSM_XML, OSM_PBF, Geopackage,Shapefile,
            ThematicGPKG,ThematicSHP, KML]:
    FORMAT_NAMES[cls.name] = cls
