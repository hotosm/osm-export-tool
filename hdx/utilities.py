
def _tag_dict(foo):
    """
    Return the unique set of Tag keys from this export
    with their associated geometry types.

    Used by Job.categorised_tags (below) to categorize tags
    according to their geometry types.
    """
    # get the unique keys from the tags for this export
    #uniq_keys = list(self.tags.values('key').distinct('key'))
    uniq_keys  = set([tag['key'] for tag in foo])
    tag_dict = {}  # mapping of tags to geom_types
    for entry in uniq_keys:
        key = entry
        tag_dict['key'] = key
        #geom_types = list(self.tags.filter(key=key).values('geom_types'))
        geom_types = [x['geom_types'] for x in foo if x['key'] == key]
        geom_type_list = []
        for geom_type in geom_types:
            geom_type_list.extend([i for i in geom_type])
        tag_dict[key] = list(set(geom_type_list))  # get unique values for geomtypes
    return tag_dict

def _filters(foo):
    """
    Return key=value pairs for each tag in this export.

    Used in utils.overpass.filter to filter the export.
    """
    filters = []
    for tag in foo:
        kv = '{0}={1}'.format(tag['key'], tag['value'])
        filters.append(kv)
    return filters

def categorised_tags(foo):
    """
    Return tags mapped according to their geometry types.
    """
    points = []
    lines = []
    polygons = []
    tag_dict = _tag_dict(foo)
    for tag in tag_dict:
        for geom in tag_dict[tag]:
            if geom == 'point':
                points.append(tag)
            if geom == 'line':
                lines.append(tag)
            if geom == 'polygon':
                polygons.append(tag)
    return {'points': sorted(points), 'lines': sorted(lines), 'polygons': sorted(polygons)}
