import logging
import pdb
from collections import OrderedDict
from lxml import etree
from StringIO import StringIO

logger = logging.getLogger(__name__)


class PresetParser():
    
    types = {
        'node': 'point',
        'way': 'line',
        'area': 'polygon',
        'closedway': 'polygon',
        'relation': 'polygon'
    }
    
    namespaces={'ns':'http://josm.openstreetmap.de/tagging-preset-1.0'}
    
    def __init__(self, preset=None, *args, **kwargs):
        self.preset = preset
        self.tags = []
    
    def parse(self, merge_with_defaults=False):
        """
        Reads in the JOSM Preset.
        Picks out all <item> elements.
        For each <item>, gets the 'type' attribute and maps the
        geometry type to the <item>'s 'key' attribute (tag name).
        Ignores <item>'s with no 'type' attribute.
        """
        f = open(self.preset)
        xml = f.read()
        tree = etree.parse(StringIO(xml))
        items = tree.xpath('//ns:item', namespaces=self.namespaces)
        for item in items:
            self.process_item_and_children(item)
        #tags = OrderedDict(sorted(self.tags.items()))
        if merge_with_defaults:
            return self.merge_presets(tags)
        else:
            return self.tags
        
    def process_item_and_children(self, item, geometrytype=None):
        geometrytypes = None
        if item.get('type'):
            item_type = item.get('type')
            geometrytypes = self.get_geometrytype(item_type)
        
        keys = item.xpath('./ns:key', namespaces=self.namespaces)
        if len(keys) > 0 and geometrytypes:
            if keys[0].get('key'):
                # get kv pair
                key = keys[0].get('key')
                value = keys[0].get('value')
                tag = {}
                tag['key'] = key
                tag['value'] = value
                geom_types = []
                for geomtype in geometrytypes:
                    geom_types.append(geomtype)
                tag['geom_types'] = list(set(geom_types))
                self.tags.append(tag)
        for child in list(item):
            self.process_item_and_children(child)

    def get_geometrytype(self, item_type):
        geometrytypes = []
        osmtypes = item_type.split(',')
        for osmtype in osmtypes:
            geometrytypes.append(self.types[osmtype])
        return geometrytypes
    
    def build_hdm_preset_dict(self, ):
        hdm = {}
        xml = StringIO(open(self.preset).read())
        tree = etree.parse(xml)
        groups = tree.xpath('./ns:group', namespaces=self.namespaces)
        for group in groups:
            name = group.get('name')
            group_dict = {}
            hdm[name] = group_dict
            self._parse_group(group, group_dict)
        return OrderedDict(sorted(hdm.items()))
        
                
    def _parse_group(self, group, group_dict):
        items = group.xpath('./ns:item', namespaces=self.namespaces)
        for item in items:
            item_dict = {}
            name = item.get('name')
            types = item.get('type') # get the type attr on the item element
            if types == None: continue # pass those items with no geom type
            geom_types = self.get_geometrytype(types)
            keys = item.xpath('./ns:key', namespaces=self.namespaces)
            if not len(keys) > 0:
                continue
            key = keys[0]
            item_dict['displayName'] = name
            item_dict['tag'] = '{0}:{1}'.format(key.get('key'), key.get('value'))
            item_dict['geom'] = geom_types
            group_dict[name] = OrderedDict(sorted(item_dict.items()))
        groups = group.xpath('./ns:group', namespaces=self.namespaces)
        for sub_group in groups:
            sub_group_dict = {}
            name = sub_group.get('name')
            group_dict[name] = sub_group_dict
            self._parse_group(sub_group, sub_group_dict)
        
        