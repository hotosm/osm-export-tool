import logging
from xml.dom.minidom import parse
import xml.dom.minidom
from collections import OrderedDict

logger = logging.getLogger(__name__) 


class PresetParser():
    
    types = {
        'node': 'point',
        'way': 'line',
        'closedway': 'polygon',
        'relation': 'polygon'
    }
    
    def __init__(self, preset=None, *args, **kwargs):
        self.preset = preset
        self.tags = {}
    
    def parse(self, ):
        dom = xml.dom.minidom.parse(self.preset)
        root = dom.documentElement
        if not root.tagName == 'presets':
            raise Exception('Not a preset file.')
        
        items = root.getElementsByTagName("item")
        for item in items:
            self.process_item_and_children(item)
        tags = OrderedDict(sorted(self.tags.items()))
        return tags
        
    def process_item_and_children(self, item, geometrytype=None):
        geometrytypes = None
        if item.hasAttribute('type'):
            item_type = item.getAttribute('type')
            geometrytypes = self.get_geometrytype(item_type)
        
        keys = item.getElementsByTagName('key')
        if len(keys) > 0 and geometrytypes:
            if keys[0].hasAttribute('key'):
                key = keys[0].getAttribute('key')
                if not key in self.tags:
                    self.tags[key] = {}
                for geomtype in geometrytypes:
                    self.tags[key][geomtype] = True # why?
        for child in item.childNodes:
            if child.nodeType == 'ELEMENT_NODE':
                self.process_item_and_children(child)
        

    def get_geometrytype(self, item_type):
        geometrytypes = []
        osmtypes = item_type.split(',')
        for osmtype in osmtypes:
            geometrytypes.append(self.types[osmtype])
        return geometrytypes
       

