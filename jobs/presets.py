# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict
from StringIO import StringIO

from lxml import etree

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

    def parse(self,):
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
        return self.tags

    def process_item_and_children(self, item, geometrytype=None):
        geometrytypes = None
        if item.get('type'):
            item_type = item.get('type')
            geometrytypes = self.get_geometrytype(item_type)
        keys = item.xpath('./ns:key', namespaces=self.namespaces)
        item_groups = {}
        groups = []
        for group in item.iterancestors(tag='{http://josm.openstreetmap.de/tagging-preset-1.0}group'):
            groups.append(group.get('name'))
        if len(keys) > 0 and geometrytypes:
            if keys[0].get('key'):
                # get kv pair
                key = keys[0].get('key')
                value = keys[0].get('value')
                tag = {}
                tag['name'] = item.get('name')
                tag['key'] = key
                tag['value'] = value
                geom_types = []
                for geomtype in geometrytypes:
                    geom_types.append(geomtype)
                tag['geom_types'] = list(set(geom_types))
                tag['groups'] = list(reversed(groups))
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


class TagParser():

    namespaces={'ns':'http://josm.openstreetmap.de/tagging-preset-1.0'}
    nsmap = {None: 'http://josm.openstreetmap.de/tagging-preset-1.0'}

    types = {
        'point': 'node',
        'line': 'way',
        'polygon': 'area,closedway,relation',
    }

    def __init__(self, tags=None, *args, **kwargs):
        self.tags = tags

    def parse_tags(self, ):
        root = etree.Element('presets', nsmap=self.nsmap)
        doc = etree.ElementTree(root)
        for tag in self.tags:
            groups = self._add_groups(root, tag)
        xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        return xml

    def _add_groups(self, parent, tag):
        for group in tag.groups:
            # check if element exists if not create it
            found_groups = parent.xpath('group[@name="' + group + '"]', namespaces=self.namespaces)
            if len(found_groups) == 0:
                grp = etree.SubElement(parent, 'group', name=group)
                tag.groups.pop(0)
                if len(tag.groups) == 0:
                    geom_types = self._get_types(tag.geom_types)
                    item = etree.SubElement(grp, 'item', name=tag.name, type=geom_types)
                    etree.SubElement(item, 'key', key=tag.key, value=tag.value)
                self._add_groups(grp, tag)
            else:
                tag.groups.pop(0)
                if len(tag.groups) == 0:
                    geom_types = self._get_types(tag.geom_types)
                    item = etree.SubElement(found_groups[0], 'item', name=tag.name, type=geom_types)
                    etree.SubElement(item, 'key', key=tag.key, value=tag.value)
                self._add_groups(found_groups[0], tag)

    def _get_types(self, geom_types):
        types = []
        for geom_type in geom_types:
            gtype = self.types.get(geom_type)
            if gtype is not None:
                types.append(self.types[geom_type])
        return ','.join(types)
