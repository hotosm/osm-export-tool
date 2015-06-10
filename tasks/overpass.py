import logging
import os
from osgeo import ogr, osr, gdal

logger = logging.getLogger(__name__)


class OSMParser(object):
    
    highway_zindex = {}
    highway_zindex["minor"] = 3;
    highway_zindex["road"] = 3;
    highway_zindex["unclassified"] = 3;
    highway_zindex["residential"] = 3;
    highway_zindex["tertiary_link"] = 4;
    highway_zindex["tertiary"] = 4;
    highway_zindex["secondary_link"] = 6;
    highway_zindex["secondary"] = 6;
    highway_zindex["primary_link"] = 7;
    highway_zindex["primary"] = 7;
    highway_zindex["trunk_link"] = 8;
    highway_zindex["trunk"] = 8;
    highway_zindex["motorway_link"] = 9;
    highway_zindex["motorway"] = 9;
    
    
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
        gdal.SetConfigOption('OGR_INTERLEAVED_READING', 'YES')
        
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
        
    def process_points(self, ):
        layerDefinition = self.points.GetLayerDefn()
        # create the schema for the planet_osm_point layer
        # TODO: only create user defined tags here..
        for i in range(0, layerDefinition.GetFieldCount()):
            fieldDefn = layerDefinition.GetFieldDefn(i)
            if fieldDefn.GetName() == 'osm_id':
                fieldDefn.SetWidth(11)
            else:
                fieldDefn.SetWidth(255)
            self.planet_osm_point.CreateField(fieldDefn)
        # add zindex field
        zindex = ogr.FieldDefn('z_index', ogr.OFTInteger)
        self.planet_osm_point.CreateField(zindex)
        counter = 0
        planet_osm_defn = self.planet_osm_point.GetLayerDefn()
        for point in self.points:
            counter = counter + 1
            outFeature = ogr.Feature(planet_osm_defn)
            zidx = self.calculate_zindex(point)
            outFeature.SetField('z_index', zidx) 
            for i in range(0, planet_osm_defn.GetFieldCount()):
                fieldDefn = planet_osm_defn.GetFieldDefn(i)
                fieldName = fieldDefn.GetName()
                outField = point.GetField(i)
                if outField != None:
                    outFeature.SetField(planet_osm_defn.GetFieldDefn(i).GetNameRef(),
                    point.GetField(i))
            self.planet_osm_point.CreateFeature(outFeature)
        self.data_source.Destroy()
        print 'processed %s nodes' % counter
        
        
    def process_lines(self, ):
        line = self.lines.GetNextFeature()
        logger.debug(line.DumpReadable())
        """
        for line in self.lines:
            logger.debug(line.DumpReadable())
        """
        
    def process_polygons(self, ):
        polygon = self.polygons.GetNextFeature()
        logger.debug(polygon.DumpReadable())
        """
        for polygon in sel.polygons:
            logger.debug(polygon.DumpReadable())
        """
    
    def process_multilinestrings(self, ):
        #multiline = self.multilines.GetNextFeature()
        #logger.debug(multiline.DumpReadable())
        count = self.multilines.GetFeatureCount()
        logger.debug(count)
    
    def process_other_relations(self, ):
        logger.debug(self.other_relations.GetFeatureCount())
        other_relation = self.other_relations.GetNextFeature()
        #logger.debug(other_relation.DumpReadable())
        
    def calculate_zindex(self, obj):
        return 1
    
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
        
if __name__ == '__main__':
    osmfile = '/home/ubuntu/www/hotosm/test.osm'
    parser = OSMParser(osmfile)
    parser.process_points()
    #parser.process_lines()
    #parser.process_polygons()
    #parser.process_multilinestrings()
    #parser.process_other_relations()
    
    
    