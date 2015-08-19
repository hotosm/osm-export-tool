import os
from django.utils import timezone

from utils.overpass import Overpass
from jobs import presets


"""
    Harness to run an Overpass Query outside of test context.
    Uses HDM datamodel to construct overpass query.
    From the project directory run:
    ./manage.py runscript overpass_benchmarks --settings=hot_exports.settings -v2
    Depends on django-extensions.
"""

def run(*script_args):
    url = 'http://localhost/interpreter'
    bbox = '6.25,-10.85,6.40,-10.62' # monrovia
    lib_bbox = '4.15,-11.60,8.55,-7.36'
    path = '/home/ubuntu/www/hotosm/utils/tests'
    osm = path + '/files/query.osm'
    tags = tags = ['amenity:fuel', 'shop:car_repair','amenity:bank',
                        'amenity:money_transfer','hazard_type:flood',
                        'landuse:residential','building:yes']
    query = '(node(6.25,-10.85,6.40,-10.62);<;);out body;'
    parser = presets.PresetParser(preset=path + '/files/hdm_presets.xml')
    geom_tags, kvps = parser.parse()
    filters = []
    for kvp in kvps:
        filter_tag = '{0}:{1}'.format(kvp[0], kvp[1])
        filters.append(filter_tag)
        
    
    print "=============="
    print "Querying Monrovia with HDM filters."
    print timezone.now()
    op = Overpass(osm=osm, bbox=bbox, tags=filters)
    op.run_query()
    print timezone.now()
    stat = os.stat(osm)
    size = stat.st_size / 1024 / 1024.00
    print 'Result file size: {0}'.format(size)
    
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
    