import math
from collections import namedtuple
from django.contrib.gis.geos import GEOSGeometry, Polygon
import requests

# goals:
# for clipping efficiency, we want a < 500 point geometry.
# * geometries of < 500 points should be unchanged.
# * when geom A is simplified to B,
#   A can have areas that are missing from B.
# * therefore, buffer by 0.02 degrees if > 500 points, then simplify.
# * geometries with an excessive amount of points can't
#   be buffered efficiently, they must be simplified first.
#   so first simplify them to 0.01 degrees.


MAX_NODES = 10000000
THRESHOLD_SQKM = 1000
MAX_SQKM = 3000000
OVERPASS_COUNT_QUERY = """
[maxsize:1000000000][timeout:30][out:json];(
(
    node({0});
);
);out count;
"""

ValidateResult = namedtuple('ValidateResult',['valid','message','params','area'])

def simplify_geom(geom,force_buffer=False):
    if geom.num_coords > 10000:
        geom = geom.simplify(0.01)
    if geom.num_coords > 500 or force_buffer:
        geom = geom.buffer(0.02)
    param = 0.01
    while geom.num_coords > 500:
        geom = geom.simplify(param, preserve_topology=True)
        param = param * 2
    return geom


def get_geodesic_area(geom):
    bbox = geom.envelope
    """
    Uses the algorithm to calculate geodesic area of a polygon from OpenLayers 2.
    See http://bit.ly/1Mite1X.

    Args:
        geom (GEOSGeometry): the export extent as a GEOSGeometry.

    Returns
        area (float): the geodesic area of the provided geometry.
    """
    area = 0.0
    coords = bbox.coords[0]
    length = len(coords)
    if length > 2:
        for x in range(length - 1):
            p1 = coords[x]
            p2 = coords[x+1]
            area += math.radians(p2[0] - p1[0]) * (2 + math.sin(math.radians(p1[1]))
                                                   + math.sin(math.radians(p2[1])))
        area = abs(int(area * 6378137 * 6378137 / 2.0 / 1000 / 1000))
    return area

def check_extent(aoi,url):
    if not aoi.valid:
        return ValidateResult(False,aoi.valid_reason,None,None)
    # because overpass queries by total extent bbox, check area against extent (example:diagonal shaped area)
    area = get_geodesic_area(Polygon.from_bbox(aoi.extent))
    if area >  MAX_SQKM:
        return ValidateResult(False,"Geometry too large: %(area)s sq km, max %(max)s",{'area': area, 'max': MAX_SQKM},area)
    if area > THRESHOLD_SQKM:
        west = max(aoi.extent[0], -180)
        south = max(aoi.extent[1], -90)
        east = min(aoi.extent[2], 180)
        north = min(aoi.extent[3], 90)
        geom = '{1},{0},{3},{2}'.format(west, south, east, north)
        query = OVERPASS_COUNT_QUERY.format(geom)
        req = requests.post('{}interpreter'.format(url),data=query,timeout=40)
        j = req.json()
        if 'remark' in j:
            return ValidateResult(False,"Could not retrieve # of nodes in this area, it is likely too large. Please choose a smaller area.",
                    {},
                    area)
        nodes = int(j['elements'][0]['tags']['nodes'])
        print nodes
        if nodes > MAX_NODES:
            return ValidateResult(False, "The selected area's bounding box contains %(nodes)s nodes.\
                The maximum is %(maxnodes)s. Please choose a smaller area.",
                {'nodes':nodes,'maxnodes':MAX_NODES},
                area
            )
    return ValidateResult(True,None,None,area)
