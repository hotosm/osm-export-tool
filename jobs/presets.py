import logging
#from xml.dom.minidom import parse
#import xml.dom.minidom
from collections import OrderedDict
from lxml import etree
from StringIO import StringIO

logger = logging.getLogger(__name__)

DEFAULT_TAGS = OrderedDict({
        "access"             : { "point": 'true', "line": 'true' },
        "addr:housename"     : { "point": 'true', "line": 'true' },
        "addr:housenumber"   : { "point": 'true', "line": 'true' },
        "addr:interpolation" : { "point": 'true', "line": 'true' },
        "admin_level"        : { "point": 'true', "line": 'true' },
        "aerialway"          : { "point": 'true', "line": 'true' },
        "aeroway"            : { "point": 'true', "polygon": 'true'},
        "amenity"            : { "point": 'true', "polygon": 'true'},
        "barrier"            : { "point": 'true', "line": 'true'},
        "bicycle"            : { "point": 'true'},
        "bridge"             : { "point": 'true', "line": 'true' },
        "boundary"           : { "point": 'true', "line": 'true' },
        "building"           : { "point": 'true', "polygon": 'true' },
        "capital"            : { "point": 'true' },
        "construction"       : { "point": 'true', "line": 'true' },
        "covered"            : { "point": 'true', "line": 'true' },
        "cutting"            : { "point": 'true', "line": 'true' },
        "denomination"       : { "point": 'true', "line": 'true' },
        "disused"            : { "point": 'true', "line": 'true' },
        "ele"                : { "point": 'true' },
        "embankment"         : { "point": 'true', "line": 'true' },
        "foot"               : { "point": 'true', "line": 'true' },
        "generator:source"   : { "point": 'true', "line": 'true' },
        "harbour"            : { "point": 'true', "polygon": 'true' },
        "highway"            : { "point": 'true', "line": 'true' },
        "historic"           : { "point": 'true', "polygon": 'true' },
        "junction"           : { "point": 'true', "line": 'true' },
        "landuse"            : { "point": 'true', "polygon": 'true' },
        "layer"              : { "point": 'true', "line": 'true' },
        "leisure"            : { "point": 'true', "polygon": 'true' },
        "lock"               : { "point": 'true', "line": 'true' },
        "man_made"           : { "point": 'true', "polygon": 'true' },
        "military"           : { "point": 'true', "polygon": 'true' },
        "motorcar"           : { "point": 'true', "line": 'true' },
        "name"               : { "point": 'true', "line": 'true' },
        "natural"            : { "point": 'true', "polygon": 'true' },
        "oneway"             : { "point": 'true', "line": 'true' },
        "poi"                : { "point": 'true' },
        "population"         : { "point": 'true', "line": 'true' },
        "power"              : { "point": 'true', "polygon": 'true' },
        "place"              : { "point": 'true', "polygon": 'true' },
        "railway"            : { "point": 'true', "line": 'true' },
        "ref"                : { "point": 'true', "line": 'true' },
        "religion"           : { "point": 'true' },
        "route"              : { "point": 'true', "line": 'true' },
        "service"            : { "point": 'true', "line": 'true' },
        "shop"               : { "point": 'true', "polygon": 'true' },
        "sport"              : { "point": 'true', "polygon": 'true' },
        "surface"            : { "point": 'true', "line": 'true' },
        "toll"               : { "point": 'true', "line": 'true' },
        "tourism"            : { "point": 'true', "polygon": 'true' },
        "tower:type"         : { "point": 'true', "line": 'true' },
        "tracktype"          : { "line": 'true' },
        "tunnel"             : { "point": 'true', "line": 'true' },
        "water"              : { "point": 'true', "polygon": 'true' },
        "waterway"           : { "point": 'true', "polygon": 'true' },
        "wetland"            : { "point": 'true', "polygon": 'true' },
        "width"              : { "point": 'true', "line": 'true' },
        "wood"               : { "point": 'true', "line": 'true' },
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
    
    def parse(self, merge_with_defaults=False):
        f = open(self.preset)
        xml = f.read()
        tree = etree.parse(StringIO(xml))
        items = tree.xpath('//ns:item', namespaces=self.namespaces)
        for item in items:
            self.process_item_and_children(item)
        tags = OrderedDict(sorted(self.tags.items()))
        if merge_with_defaults:
            return self.merge_presets(tags)
        else:
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
                    self.tags[key][geomtype] = 'true'
        for child in list(item):
            self.process_item_and_children(child)

    def get_geometrytype(self, item_type):
        geometrytypes = []
        osmtypes = item_type.split(',')
        for osmtype in osmtypes:
            geometrytypes.append(self.types[osmtype])
        return geometrytypes
       
    def merge_presets(self, tags):
        merged_tags = DEFAULT_TAGS.copy()
        user_tags = tags.copy()
        merged_tags.update(user_tags)
        return merged_tags
    
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
        return {'points': sorted(points), 'lines': sorted(lines), 'polygons': sorted(polygons)}
                
            
            
        
    

