import logging
#from xml.dom.minidom import parse
#import xml.dom.minidom
from collections import OrderedDict
from lxml import etree
from StringIO import StringIO

logger = logging.getLogger(__name__)

DEFAULT_TAGS = OrderedDict({
        "access"             : { "point": True, "line": True },
        "addr:housename"     : { "point": True, "line": True },
        "addr:housenumber"   : { "point": True, "line": True },
        "addr:interpolation" : { "point": True, "line": True },
        "admin_level"        : { "point": True, "line": True },
        "aerialway"          : { "point": True, "line": True },
        "aeroway"            : { "point": True, "polygon": True},
        "amenity"            : { "point": True, "polygon": True},
        "barrier"            : { "point": True, "line": True},
        "bicycle"            : { "point": True},
        "bridge"             : { "point": True, "line": True },
        "boundary"           : { "point": True, "line": True },
        "building"           : { "point": True, "polygon": True },
        "capital"            : { "point": True },
        "construction"       : { "point": True, "line": True },
        "covered"            : { "point": True, "line": True },
        "cutting"            : { "point": True, "line": True },
        "denomination"       : { "point": True, "line": True },
        "disused"            : { "point": True, "line": True },
        "ele"                : { "point": True },
        "embankment"         : { "point": True, "line": True },
        "foot"               : { "point": True, "line": True },
        "generator:source"   : { "point": True, "line": True },
        "harbour"            : { "point": True, "polygon": True },
        "highway"            : { "point": True, "line": True },
        "historic"           : { "point": True, "polygon": True },
        "junction"           : { "point": True, "line": True },
        "landuse"            : { "point": True, "polygon": True },
        "layer"              : { "point": True, "line": True },
        "leisure"            : { "point": True, "polygon": True },
        "lock"               : { "point": True, "line": True },
        "man_made"           : { "point": True, "polygon": True },
        "military"           : { "point": True, "polygon": True },
        "motorcar"           : { "point": True, "line": True },
        "name"               : { "point": True, "line": True },
        "natural"            : { "point": True, "polygon": True },
        "oneway"             : { "point": True, "line": True },
        "poi"                : { "point": True },
        "population"         : { "point": True, "line": True },
        "power"              : { "point": True, "polygon": True },
        "place"              : { "point": True, "polygon": True },
        "railway"            : { "point": True, "line": True },
        "ref"                : { "point": True, "line": True },
        "religion"           : { "point": True },
        "route"              : { "point": True, "line": True },
        "service"            : { "point": True, "line": True },
        "shop"               : { "point": True, "polygon": True },
        "sport"              : { "point": True, "polygon": True },
        "surface"            : { "point": True, "line": True },
        "toll"               : { "point": True, "line": True },
        "tourism"            : { "point": True, "polygon": True },
        "tower:type"         : { "point": True, "line": True },
        "tracktype"          : { "line": True },
        "tunnel"             : { "point": True, "line": True },
        "water"              : { "point": True, "polygon": True },
        "waterway"           : { "point": True, "polygon": True },
        "wetland"            : { "point": True, "polygon": True },
        "width"              : { "point": True, "line": True },
        "wood"               : { "point": True, "line": True },
})


class PresetParser():
    
    types = {
        'node': 'point',
        'way': 'line',
        'closedway': 'polygon',
        'relation': 'polygon'
    }
    namespaces={'ns':'http://josm.openstreetmap.de/tagging-preset-1.0'}
    
    def __init__(self, preset=None, *args, **kwargs):
        self.preset = preset
        self.tags = {}
    
    def parse(self, ):
        f = open(self.preset)
        xml = f.read()
        tree = etree.parse(StringIO(xml))
        items = tree.xpath('//ns:item', namespaces=self.namespaces)
        for item in items:
            self.process_item_and_children(item)
        tags = OrderedDict(sorted(self.tags.items()))
        return tags
        
    def process_item_and_children(self, item, geometrytype=None):
        geometrytypes = None
        if item.get('type'):
            item_type = item.get('type')
            geometrytypes = self.get_geometrytype(item_type)
        
        keys = item.xpath('./ns:key', namespaces=self.namespaces)
        if len(keys) > 0 and geometrytypes:
            if keys[0].get('key'):
                key = keys[0].get('key')
                if not key in self.tags:
                    self.tags[key] = {}
                for geomtype in geometrytypes:
                    self.tags[key][geomtype] = True
        for child in list(item):
            self.process_item_and_children(child)

    def get_geometrytype(self, item_type):
        geometrytypes = []
        osmtypes = item_type.split(',')
        for osmtype in osmtypes:
            geometrytypes.append(self.types[osmtype])
        return geometrytypes
       
    def merge_presets(self, tags):
        x = DEFAULT_TAGS.copy()
        tags.update(x)
        return tags
    
    def categorise_tags(self, tags):
        points = []
        lines = []
        polygons = []
        for tag in tags.keys():
            for geom in tags[tag].keys():
                if geom == 'point':
                    points.append(tag)
                if geom == 'line':
                    lines.append(tag)
                if geom == 'polygon':
                    polygons.append(tag)
        return {'points': points, 'lines': lines, 'polygons': polygons}
                
            
            
        
    

