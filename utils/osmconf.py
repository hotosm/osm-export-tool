import ConfigParser
import os
import logging

logger = logging.getLogger(__name__)


class EqualsSpaceRemover:
    """
    Removes spaces from around '=' which
    causes ogr2ogr to ignore required attributes.
    """
    output_file = None
    def __init__( self, new_output_file ):
        self.output_file = new_output_file

    def write( self, what ):
        self.output_file.write( what.replace( " = ", "=" ))


class OSMConfig(object):
    """
    Creates ogr2ogr OSM conf file based on the template
    at utils/conf/hotosm.ini.tmpl
    """
    def __init__(self, categories=None):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.tmpl = self.path + '/conf/hotosm.ini.tmpl'
        self.categories = categories
        self.config = ConfigParser.SafeConfigParser()
        
    def create_osm_conf(self, stage_dir=None):
        self.config.read(self.tmpl) # read in the template
        self.config.set('points', 'attributes', ','.join(self.categories['points']))
        self.config.set('lines', 'attributes', ','.join(self.categories['lines']))
        self.config.set('multipolygons', 'attributes', ','.join(self.categories['polygons']))
        # write the out the config
        config_file = stage_dir + 'osmconf.ini'
        with open(config_file, 'wb') as configfile:
            self.config.write(EqualsSpaceRemover(configfile))
        return config_file
        
        
    
    
    
    
    