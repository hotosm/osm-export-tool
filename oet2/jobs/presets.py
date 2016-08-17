# -*- coding: utf-8 -*-
import logging
import pdb
from collections import OrderedDict
from StringIO import StringIO

from lxml import etree

logger = logging.getLogger(__name__)


class PresetParser():
    """
    Create Tag model instances from HDM or OSM presets.

    Uses primarily in api.views.JobViewSet.create to parse out
    the default set of tags for export creation if no presets
    or tags are provided by the user.

    Parsing by this parser is more restrictive in that it looks for
    'key' elements of each 'item' element and uses these to construct
    the Tag instances. 
    """

    types = {
        'node': 'point',
        'way': 'line',
        'area': 'polygon',
        'closedway': 'polygon',
        'relation': 'polygon'
    }

    namespaces = {'ns': 'http://josm.openstreetmap.de/tagging-preset-1.0'}

    def __init__(self, preset=None, *args, **kwargs):
        """Initialize the parser with the preset."""
        self.preset = preset
        self.tags = []

    def parse(self,):
        """Read in the JOSM Preset and processes the 'item' elements."""
        f = open(self.preset)
        xml = f.read()
        tree = etree.parse(StringIO(xml))
        items = tree.xpath('//ns:item', namespaces=self.namespaces)
        for item in items:
            self.process_item_and_children(item)
        # tags = OrderedDict(sorted(self.tags.items()))
        return self.tags

    def process_item_and_children(self, item, geometrytype=None):
        """
        Process the 'item' elements in the preset.

        Gets the 'type' attribute from the 'item' element.
        Gets the geometrytype (point/line/polygon) of the 'type' attribute.
        Keeps track of all ancestor 'group' elements of the 'item'.
        Only processes 'item' elements that have a 'type' attribute.
        For each 'key' child element of the 'item', construct a Tag instance.

        The Tag holds:
            1. the name of the 'item'
            2. the value of the 'key' attribute.
            3. the value of the 'value' attribute, eg 'highway=motorway'
            4. the geometrytypes that this tag supports (point/line/polygon)
            5. the ancestor 'group' elements of this 'item'
                - This is done so we can reconstruct the preset from the users tag selection
        """
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
        """
        Builds a python dict to represent the
        hierarchy of 'group' and 'item' elements
        in a JOSM preset.

        Used in api.views.HDMDataModelView and OSMDataModelView
        to serialize the HDM and OSM data models to JSON for
        the UI tag selection trees.

        See:
            http://export.hotosm.org/api/hdm-data-model?format=json
            http://export.hotosm.org/api/osm-data-model?format=json
        """
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
        # pull out 'item' subelements from parent 'group'.
        # map the 'items' to their parent 'group'.
        items = group.xpath('./ns:item', namespaces=self.namespaces)
        for item in items:
            item_dict = {}
            name = item.get('name')
            types = item.get('type')  # get the type attr on the item element
            if types == None:
                continue  # pass those items with no geom type
            geom_types = self.get_geometrytype(types)
            keys = item.xpath('./ns:key', namespaces=self.namespaces)
            if not len(keys) > 0:
                continue
            key = keys[0]
            item_dict['displayName'] = name
            item_dict['tag'] = '{0}={1}'.format(key.get('key'), key.get('value'))
            item_dict['geom'] = geom_types
            group_dict[name] = OrderedDict(sorted(item_dict.items()))
        # pull out subgroups of this group and recursively process
        groups = group.xpath('./ns:group', namespaces=self.namespaces)
        for sub_group in groups:
            sub_group_dict = {}
            name = sub_group.get('name')
            group_dict[name] = sub_group_dict
            self._parse_group(sub_group, sub_group_dict)


class UnfilteredPresetParser():
    """
    Parses uploaded JOSM Presets and creates Tag model instances based on
    the contents of the preset file. See jobs.models.Tag for the instance fields.

    Looks for the 'key', 'text', 'combo', 'multiselect' and 'check' child
    elements of all 'item' elements in the preset. Pulls out the 'key' attribute
    of these elements.
    """

    types = {
        'node': 'point',
        'way': 'line',
        'area': 'polygon',
        'closedway': 'polygon',
        'relation': 'polygon'
    }

    supported_elements = ['key', 'text', 'combo', 'multiselect', 'check']

    namespaces = {'ns': 'http://josm.openstreetmap.de/tagging-preset-1.0'}

    def __init__(self, preset=None, *args, **kwargs):
        """Initialize the parser with the preset."""
        self.preset = preset
        self.tags = []
        self.keys = []

    def parse(self,):
        """Read in the JOSM Preset and processes the 'item' elements."""
        f = open(self.preset)
        xml = f.read()
        tree = etree.parse(StringIO(xml))
        # pull out all items
        items = tree.xpath('//ns:item', namespaces=self.namespaces)
        # iterate throught the item elements and process them
        for item in items:
            self.process_item_and_children(item)
        # tags = OrderedDict(sorted(self.tags.items()))
        return self.tags

    def process_item_and_children(self, item, geometrytype=None):
        """
        Process the 'item' elements in the preset.

        Gets the 'type' attribute from the 'item' element.
        Gets the geometrytype (point/line/polygon) of the 'type' attribute.
        Keeps track of all ancestor 'group' elements of the 'item'.
        Only processes 'item' elements that have a 'type' attribute.
        For each supported_element child of the 'item', construct a Tag instance.

        The Tag holds:
            1. the name of the 'item'
            2. the value of the 'key' attribute.
            3. the blank/unfiltered 'value' so that we pull out all values for each 'key',eg highway=*
            4. the geometrytypes that this tag supports (point/line/polygon)
            5. the ancestor 'group' elements of this 'item'
               We do this if we need to reconstruct the preset from the users tag selection.
        """
        geometrytypes = None
        if item.get('type'):
            item_type = item.get('type')
            geometrytypes = self.get_geometrytype(item_type)
        elements = item.xpath('./ns:*', namespaces=self.namespaces)
        item_groups = {}
        groups = []
        for group in item.iterancestors(tag='{http://josm.openstreetmap.de/tagging-preset-1.0}group'):
            groups.append(group.get('name'))
        if len(elements) > 0 and geometrytypes:
            for element in elements:
                name = element.xpath('local-name()')
                if name in self.supported_elements:
                    key = element.get('key')
                    if key in self.keys:
                        continue  # skip key if already parsed
                    tag = {}
                    tag['name'] = item.get('name')
                    tag['key'] = key
                    tag['value'] = ''  # select all not-null values
                    geom_types = []
                    for geomtype in geometrytypes:
                        geom_types.append(geomtype)
                    tag['geom_types'] = list(set(geom_types))
                    tag['groups'] = list(reversed(groups))
                    self.tags.append(tag)
                    self.keys.append(key)
        for child in list(item):
            self.process_item_and_children(child)

    def get_geometrytype(self, item_type):
        """
        Maps OSM geometry types [node,way,rel] to [point,line,polygon]

        This is used by OSMConf task to filter tags based on their geometry type,
        eg, planet_osm_line, planet_osm_polygon etc.
        """
        geometrytypes = []
        osmtypes = item_type.split(',')
        for osmtype in osmtypes:
            geometrytypes.append(self.types[osmtype])
        return geometrytypes

    def build_hdm_preset_dict(self, ):
        """
        NOT USED AT PRESENT EXCEPT IN TESTS.

        Builds a python dict to represent the
        hierarchy of 'group' and 'item' elements
        in a JOSM preset.

        Used in api.views.HDMDataModelView and OSMDataModelView
        to serialize the HDM and OSM data models to JSON for
        the UI tag selection trees.

        See:
            http://export.hotosm.org/api/hdm-data-model?format=json
            http://export.hotosm.org/api/osm-data-model?format=json
        """
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
        """Parse child 'item' elements for the parent group."""
        items = group.xpath('./ns:item', namespaces=self.namespaces)
        for item in items:
            item_dict = {}
            name = item.get('name')
            types = item.get('type')  # get the type attr on the item element
            if types == None:
                continue  # pass those items with no geom type

            # map osm geomtypes to point, line, polygon geom types
            geom_types = self.get_geometrytype(types)
            # pull out key sub elements
            keys = item.xpath('./ns:key', namespaces=self.namespaces)
            if not len(keys) > 0:
                continue
            key = keys[0]
            item_dict['displayName'] = name
            item_dict['tag'] = '{0}={1}'.format(key.get('key'), key.get('value'))
            item_dict['geom'] = geom_types
            group_dict[name] = OrderedDict(sorted(item_dict.items()))
        groups = group.xpath('./ns:group', namespaces=self.namespaces)
        for sub_group in groups:
            sub_group_dict = {}
            name = sub_group.get('name')
            group_dict[name] = sub_group_dict
            self._parse_group(sub_group, sub_group_dict)


class TagParser():
    """
    Reconstruct a JOSM Preset from the users selected Tag's.

    Used in tasks.export_tasks.GeneratePresetTask.
    """
    namespaces = {'ns': 'http://josm.openstreetmap.de/tagging-preset-1.0'}
    nsmap = {None: 'http://josm.openstreetmap.de/tagging-preset-1.0'}

    types = {
        'point': 'node',
        'line': 'way',
        'polygon': 'closedway,relation',
    }

    def __init__(self, tags=None, *args, **kwargs):
        """Initialized with a list of users tag selection."""
        self.tags = tags

    def parse_tags(self, ):
        """
        Construct the preset xml document.

        Add the root 'presets' element.
        Iterate through the groups for each tag in the users tags
        to construct the group element along with its child 'item' elements.

        Retuns:
            the generated preset xml file.
        """
        root = etree.Element('presets', nsmap=self.nsmap)
        doc = etree.ElementTree(root)
        for tag in self.tags:
            groups = self._add_groups(root, tag)
        xml = etree.tostring(doc, xml_declaration=True, encoding='UTF-8', pretty_print=True)
        return xml

    def _add_groups(self, parent, tag):
        """
        Add the 'group' elements to the preset xml document.

        Recursively iterate through the groups for the provided tag and reconstruct
        the group element and its child item elements. The 'item' elements
        get their child 'key' elements added in turn.
        """
        for group in tag.groups:
            # check if this group element exists already, if not create it...
            found_groups = parent.xpath('group[@name="' + group + '"]', namespaces=self.namespaces)
            if len(found_groups) == 0:
                # create a new group element on the document
                grp = etree.SubElement(parent, 'group', name=group)
                # remove this group from the tag so we don't duplicate it
                tag.groups.pop(0) 
                if len(tag.groups) == 0:
                    # get the osm geometry types for this tag
                    geom_types = self._get_types(tag.geom_types)
                    # add the item element to the group
                    item = etree.SubElement(grp, 'item', name=tag.name, type=geom_types)
                    # add the 'key' element to the 'item'
                    etree.SubElement(item, 'key', key=tag.key, value=tag.value)
                # process any subgroups of this group
                self._add_groups(grp, tag)
            else:
                # the group exists in the xml already
                tag.groups.pop(0)
                if len(tag.groups) == 0:
                    # get the osm geometry type for this group
                    geom_types = self._get_types(tag.geom_types)
                    # add another item to the found group
                    item = etree.SubElement(found_groups[0], 'item', name=tag.name, type=geom_types)
                    # add the 'key' child element to the 'item'
                    etree.SubElement(item, 'key', key=tag.key, value=tag.value)
                # process any subgroups of this group
                self._add_groups(found_groups[0], tag)

    def _get_types(self, geom_types):
        """
        Maps the Tags geomtypes back to OSM geometry types.
        """
        types = []
        for geom_type in geom_types:
            gtype = self.types.get(geom_type)
            if gtype is not None and gtype not in types:
                types.append(self.types[geom_type])
        return ','.join(types)
