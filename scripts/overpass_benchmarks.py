import os

from django.utils import timezone

from oet2.jobs import presets
from utils.overpass import Overpass


"""
    Harness to run an Overpass Query outside of test context.
    Uses HDM/OSM Data Models to construct overpass query.
    From the project directory run:
    ./manage.py runscript overpass_benchmarks --settings=hot_exports.settings -v2
    Depends on django-extensions.
"""


def run(*script_args):
    url = 'http://localhost/interpreter'
    bbox = '6.25,-10.85,6.40,-10.62'  # monrovia
    lib_bbox = '4.15,-11.60,8.55,-7.36'
    path = '/home/ubuntu/www/hotosm/utils/tests'
    query = '(node(6.25,-10.85,6.40,-10.62);<;);out body;'
    parser = presets.PresetParser(preset=path + '/files/osm_presets.xml')
    kvps = parser.parse()
    filters = []
    for kvp in kvps:
        filter_tag = '{0}={1}'.format(kvp['key'], kvp['value'])
        filters.append(filter_tag)
    print filters

    print "=============="
    print "Querying Monrovia with OSM filters."
    print timezone.now()
    op = Overpass(
        bbox=bbox, stage_dir=path + '/files/',
        job_name='test', filters=filters
    )
    osm = op.run_query()
    print timezone.now()
    stat = os.stat(osm)
    size = stat.st_size / 1024 / 1024.00
    print 'Result file size: {0}'.format(size)

    filtered = op.filter()

    # check pbf conversion
    # pbf = OSMToPBF(osm=path + '/files/filter.osm', pbffile=path + '/files/filter.pbf', debug=True)
    # pbf.convert()

    """
    print "=============="
    print "Querying Monrovia without filters."
    print timezone.now()
    op = Overpass(osm=osm, bbox=bbox)
    op.run_query()
    print timezone.now()
    stat = os.stat(osm)
    size = stat.st_size / 1024 / 1024.00
    print 'Result file size: {0}'.format(size)


    print "=============="
    print "Querying Liberia with HDM filters."
    print timezone.now()
    op = Overpass(osm=osm, bbox=lib_bbox, tags=filters)
    op.run_query()
    print timezone.now()
    stat = os.stat(osm)
    size = stat.st_size / 1024 / 1024.00
    print 'Result file size: {0}'.format(size)


    print "=============="
    print "Querying Liberia without filters."
    print timezone.now()
    op = Overpass(osm=osm, bbox=lib_bbox)
    op.run_query()
    print timezone.now()
    stat = os.stat(osm)
    size = stat.st_size / 1024 / 1024.00
    print 'Result file size: {0}'.format(size)
    """
