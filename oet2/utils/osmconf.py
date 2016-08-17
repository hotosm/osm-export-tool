# -*- coding: utf-8 -*-
import ConfigParser
import logging
import os

logger = logging.getLogger(__name__)


class EqualsSpaceRemover:
    """
    Removes spaces from around '=' which
    causes ogr2ogr to ignore required attributes.
    """
    output_file = None

    def __init__(self, new_output_file):
        self.output_file = new_output_file

    def write(self, what):
        self.output_file.write(what.replace(" = ", "="))


class OSMConfig(object):
    """
    Create ogr2ogr OSM conf file based on the template
    at utils/conf/hotosm.ini.tmpl

    See: http://www.gdal.org/drv_osm.html
    """

    def __init__(self, categories=None, job_name=None):
        """
        Initialize the OSMConfig utility.

        Args:
            categories: the export tags categorized by geometry type.
            job_name: the name of the job
        """
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.tmpl = self.path + '/conf/hotosm.ini.tmpl'
        self.categories = categories
        self.config = ConfigParser.SafeConfigParser()
        self.job_name = job_name

    def create_osm_conf(self, stage_dir=None):
        """
        Create the osm configuration file.

        Args:
            stage_dir: where to stage the config file.

        Return:
            the path to the export configuration file.
        """
        self.config.read(self.tmpl)  # read in the template
        self.config.set('points', 'attributes', ','.join(self.categories['points']))
        self.config.set('lines', 'attributes', ','.join(self.categories['lines']))
        self.config.set('multipolygons', 'attributes', ','.join(self.categories['polygons']))
        # write the out the config
        config_file = stage_dir + self.job_name + '.ini'
        try:
            with open(config_file, 'wb') as configfile:
                self.config.write(EqualsSpaceRemover(configfile))
        except IOError as e:
            logger.error(e)
            raise IOError('Failed to create osmconf ini file.')
        return config_file
