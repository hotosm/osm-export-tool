# -*- coding: utf-8 -*-
from __future__ import with_statement

import argparse
import logging
import os
import shutil
import subprocess
import zipfile
from string import Template

LOG = logging.getLogger(__name__)

class Shapefile(object):
    """
    Convert a GeoPackage to shapefile.
    """
    name = 'shp'
    description = 'ESRI SHP (OSM Schema)'

    def __init__(self, input_gpkg, output_zip):
        """
        Initialize the GPKGToShp utility.

        Args:
            gpg: the GeoPackage to convert.
            shapefile: the path to the shapefile output
            zipped: whether to zip the output
        """
        self.gpkg = input_gpkg
        self.output_zip = output_zip
        self.cmd = Template("ogr2ogr -f 'ESRI Shapefile' $shp $gpkg -lco ENCODING=UTF-8 -overwrite -skipfailures")

    def run(self):
        """
        Convert the GeoPackage to a Shapefile.
        """
        shapefile_dir = self.output_zip[:-4]
        print shapefile_dir
        convert_cmd = self.cmd.safe_substitute({'shp': shapefile_dir, 'gpkg': self.gpkg})
        LOG.debug('Running: %s' % convert_cmd)
        proc = subprocess.check_call(convert_cmd, shell=True, executable='/bin/bash')
        with zipfile.ZipFile(self.output_zip,'w',zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(shapefile_dir):
                for f in files:
                    z.write(os.path.join(root, f),f)

        return self.output_zip

    @property
    def is_complete(self):
        return os.path.isfile(self.output_zip)
    
    @property
    def results(self):
        return [self.output_zip]
