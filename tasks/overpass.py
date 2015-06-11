import logging
import os
from osgeo import ogr, osr, gdal
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)


class OSMParser(object):
    
    highway_zindex = {}
    highway_zindex['path'] = 2
    highway_zindex['track'] = 2
    highway_zindex['footway'] = 2
    highway_zindex["minor"] = 3
    highway_zindex["road"] = 3
    highway_zindex['service'] = 3
    highway_zindex["unclassified"] = 3
    highway_zindex["residential"] = 3
    highway_zindex["tertiary_link"] = 4
    highway_zindex["tertiary"] = 4
    highway_zindex["secondary_link"] = 6
    highway_zindex["secondary"] = 6
    highway_zindex["primary_link"] = 7
    highway_zindex["primary"] = 7
    highway_zindex["trunk_link"] = 8
    highway_zindex["trunk"] = 8
    highway_zindex["motorway_link"] = 9
    highway_zindex["motorway"] = 9
    
    
    def __init__(self, osmfile):
        # open the osmfile created from overpass query
        self.osmfile = osmfile
        """
            set gdal config options: see http://www.gdal.org/drv_osm.html
            use the osm driver in gdal 1.11.2
            osmconf.ini determines which OSM attributes and keys should be translated into OGR layer fields
            see osmconf.ini for details
        """
        self.path = os.path.dirname(os.path.realpath(__file__))
        # Enable GDAL/OGR exceptions
        gdal.UseExceptions()
        #gdal.PushErrorHandler(self.gdal_error_handler)
        gdal.SetConfigOption('OSM_CONFIG_FILE', self.path + '/osmconf.ini')
        gdal.SetConfigOption('CPL_TMPDIR', '/tmp')
        gdal.SetConfigOption('OSM_MAX_TMPFILE_SIZE', '100') # default in MB
        gdal.SetConfigOption('OGR_INTERLEAVED_READING', 'NO')
        
        # pull out the default ogr created layers read in from overpass output
        self.osm = ogr.Open(self.osmfile)
        self.points = self.osm.GetLayerByName('points')
        self.lines = self.osm.GetLayerByName('lines')
        self.polygons = self.osm.GetLayerByName('multipolygons')
        self.multilines = self.osm.GetLayerByName('multilinestrings')
        self.other_relations = self.osm.GetLayerByName('other_relations')
        # create the output spatialite file and initialize the layers
        self.init_spatialite()
        
    def init_spatialite(self, ):
        # create a new spatialite file with our new planet_osm_* layers
        self.driver = ogr.GetDriverByName("SQlite")
        self.data_source = self.driver.CreateDataSource(self.path + '/test.sqlite', ('SPATIALITE','YES'))
        self.srs = osr.SpatialReference()
        self.srs.ImportFromEPSG(4326) # configurable
        self.planet_osm_point = self.data_source.CreateLayer('planet_osm_point', self.srs, ogr.wkbPoint)
        self.planet_osm_line = self.data_source.CreateLayer('planet_osm_line', self.srs, ogr.wkbLineString)
        self.planet_osm_polygon = self.data_source.CreateLayer('planet_osm_polygon', self.srs, ogr.wkbMultiPolygon)
        self.planet_osm_roads = self.data_source.CreateLayer('planet_osm_roads', self.srs, ogr.wkbLineString)
        
        # just for testing
        self.planet_osm_multiline = self.data_source.CreateLayer('multilines', self.srs, ogr.wkbMultiLineString)
        self.planet_osm_other = self.data_source.CreateLayer('other_relations', self.srs, ogr.wkbMultiPolygon)
        
    def init_layer_mapping(self,):
        self.layer_map = {
          
        }
        
    def process_points(self, ):
        self.process_features(self.points, self.planet_osm_point, 'point')
        
    def process_lines(self, ):
        self.process_features(self.lines, self.planet_osm_line, 'line')
        
    def process_polygons(self, ):
        self.process_features(self.polygons, self.planet_osm_polygon, 'polygon')
    
    def process_multilinestrings(self, ):
        self.process_features(self.multilines, self.planet_osm_multiline, 'multilinestring')
    
    def process_other_relations(self, ):
        self.process_features(self.other_relations, self.planet_osm_other, 'other_relation')

    def process_features(self, oldLayer=None, newLayer=None, layer_type=None, tags=None):
        layerDefinition = oldLayer.GetLayerDefn()
         # create the schema for the planet_osm_* layer
         # TODO: only create user defined tags here..
        for i in range(0, layerDefinition.GetFieldCount()):
            fieldDefn = layerDefinition.GetFieldDefn(i)
            if fieldDefn.GetName() == 'osm_id':
                fieldDefn.SetWidth(11)
            else:
                fieldDefn.SetWidth(255)
            newLayer.CreateField(fieldDefn)
        # add zindex field
        zindex = ogr.FieldDefn('z_index', ogr.OFTInteger)
        zindex.SetWidth(4)
        newLayer.CreateField(zindex)
        counter = 0
        planet_osm_defn = newLayer.GetLayerDefn()
        for feature in oldLayer:
            outFeature = ogr.Feature(planet_osm_defn)
            zidx = self.calculate_zindex(feature)
            outFeature.SetField('z_index', zidx)
            for i in range(0, planet_osm_defn.GetFieldCount()):
                fieldDefn = planet_osm_defn.GetFieldDefn(i)
                fieldName = fieldDefn.GetName()
                try:
                    outField = feature.GetField(i)
                except ValueError:
                    continue
                if outField != None:
                    outFeature.SetField(planet_osm_defn.GetFieldDefn(i).GetNameRef(),
                    feature.GetField(i))
            geom = feature.GetGeometryRef()
            outFeature.SetGeometry(geom.Clone())
            newLayer.CreateFeature(outFeature)
            outFeature.Destroy()
            feature.Destroy()
            counter += 1
        print 'processed {0} {1}s'.format(counter, layer_type)
        
    def calculate_zindex(self, feature):
        zidx = 0
        try:
            hway = feature.GetField('highway')
            if hway != None:
                zidx += self.highway_zindex[hway]
        except (ValueError, KeyError):
            pass
        try:
            railway = feature.GetField('railway')
            if railway != None:
                zidx += 5
        except ValueError:
            pass
        try:
            layer = feature.GetField('layer')
            if layer != None:
                zidx += 10 * int(layer)
        except ValueError:
            pass
        try:
            bridge = feature.GetField('bridge')
            if bridge != None:
                if bridge in ['yes', 'true', '1']:
                    zidx += 10
        except ValueError:
            pass
        try:
            tunnel = feature.GetField('tunnel')
            if tunnel != None:
                if tunnel in ['yes', 'true', '1']:
                    zidx -= 10
        except ValueError:
            pass
        return zidx
    
    def gdal_error_handler(err_class, err_num, err_msg):
        errtype = {
                gdal.CE_None:'None',
                gdal.CE_Debug:'Debug',
                gdal.CE_Warning:'Warning',
                gdal.CE_Failure:'Failure',
                gdal.CE_Fatal:'Fatal'
        }
        err_msg = err_msg.replace('\n',' ')
        err_class = errtype.get(err_class, 'None')
        print 'Error Number: %s' % (err_num)
        print 'Error Type: %s' % (err_class)
        print 'Error Message: %s' % (err_msg)
        
    def close_datasource(self, ):
        self.data_source.Destroy()
        self.osm.Destroy()
        
if __name__ == '__main__':
    osmfile = '/home/ubuntu/www/hotosm/test.osm'
    print datetime.now()
    parser = OSMParser(osmfile)
    parser.process_points()
    parser.process_lines()
    parser.process_polygons()
    #parser.process_multilinestrings()
    #parser.process_other_relations()
    parser.close_datasource()
    print datetime.now()
    