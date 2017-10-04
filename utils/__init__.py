from __future__ import absolute_import

from .osm_xml import OSM_XML
from .osm_pbf import OSM_PBF
from .geopackage import Geopackage
from .shp import Shapefile
from .kml import KML
from .garmin_img import GarminIMG
from .osmand_obf import OsmAndOBF
from .mbtiles import MBTiles
from .mwm import MWM
from .posm_bundle import POSMBundle
from .unfiltered_pbf import UnfilteredPBF


class ThematicShp(object):
    description = 'UNUSED/THEMATIC SHP'


class ThematicGpkg(object):
    description = 'UNUSED/THEMATIC GPKG'


FORMAT_NAMES = {}
for cls in [
        OSM_XML, OSM_PBF, Geopackage, Shapefile, KML, GarminIMG, OsmAndOBF,
        MBTiles, MWM, POSMBundle, UnfilteredPBF
]:
    FORMAT_NAMES[cls.name] = cls

FORMAT_NAMES['theme_shp'] = ThematicShp
FORMAT_NAMES['theme_gpkg'] = ThematicGpkg


def map_names_to_formats(names_list):
    return [FORMAT_NAMES[name] for name in names_list]
