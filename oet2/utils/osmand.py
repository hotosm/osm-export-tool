# -*- coding: utf-8 -*-
import argparse
import logging
import os
import shutil
import subprocess
from string import Template
from StringIO import StringIO

from lxml import etree

logger = logging.getLogger(__name__)


class UpdateBatchXML(object,):
    """
    Updates the conf/batch.xml.tmpl which configures the OSMAnd process.
    """

    def __init__(self, batch_xml=None, work_dir=None):
        """
        Initialize the batch utility.

        Args:
            batch_xml: the path to the batch_xml template
            work_dir: where to write the updated batch_xml file
        """
        self.batch_xml = batch_xml
        self.work_dir = work_dir
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir, 6600)

    def update(self,):
        """
        Update the batch_xml file with configuration.

        Return:
            the path to the updated batch_xml file.
        """
        f = open(self.batch_xml)
        xml = f.read()
        tree = etree.parse(StringIO(xml))
        process_ele = tree.xpath('//process')
        assert len(process_ele) == 1, "No 'process' element found in batch.xml"
        process_ele[0].attrib['directory_for_osm_files'] = self.work_dir
        process_ele[0].attrib['directory_for_index_files'] = self.work_dir
        process_ele[0].attrib['directory_for_generation'] = self.work_dir
        process_ele[0].attrib['skipExistingIndexesAt'] = self.work_dir
        updated_path = self.work_dir + '/batch.xml'
        with open(updated_path, 'wb') as updated:
            updated.write(
                etree.tostring(tree, encoding='utf-8', pretty_print=True)
            )
        return updated_path


class OSMToOBF(object):
    """
    Convert osm input to obf output.
    """

    def __init__(self, pbffile=None, work_dir=None,
                 map_creator_dir=None, debug=False):
        """
        Initialize the OSMToOBF utility.

        Args:
            pbffile: the osm file to convert
            work_dir: the staging dir for the conversion process
            map_creator_dir: the location of the osmand map creator utility
        """
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.pbffile = pbffile
        if not os.path.exists(self.pbffile):
            raise IOError('Cannot find PBF file for this task.')
        self.work_dir = work_dir
        self.map_creator_dir = map_creator_dir
        self.debug = debug
        self.batch_xml = self.path + '/conf/batch.xml.tmpl'
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir, 6600)
        self.obf_cmd = Template("""
            cd $map_creator_dir && \
            java -Djava.util.logging.config.file=logging.properties \
                -Xms256M -Xmx1024M -cp "./OsmAndMapCreator.jar:./lib/OsmAnd-core.jar:./lib/*.jar" \
                net.osmand.data.index.IndexBatchCreator $batch_xml
        """)

    def convert(self,):
        """
        Perform the conversion from PBF to OBF.
        """
        # create the batch.xml file in the staging dir
        batch_update = UpdateBatchXML(
            batch_xml=self.batch_xml, work_dir=self.work_dir
        )
        updated_batch = batch_update.update()
        shutil.copy(self.pbffile, self.work_dir + '/query.osm.pbf')
        osmand_cmd = self.obf_cmd.safe_substitute(
            {'map_creator_dir': self.map_creator_dir,
             'batch_xml': updated_batch}
        )
        if(self.debug):
            print 'Running: %s' % osmand_cmd
        proc = subprocess.Popen(osmand_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        """
        Need a way to catch exceptions here...
        if (stderr != None and not stderr.startswith('INFO')):
                logger.debug(stderr.rstrip())
                raise Exception, "OsmAndMapCreator process failed with error: %s" % stderr.rstrip()
        """
        returncode = proc.wait()
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, "{0} process failed with returncode: {1}".format(osmand_cmd, returncode)
        if self.debug:
            print 'OsmAndMapCreator returned: %s' % returncode
        obffile = None
        for f in os.listdir(self.work_dir):
            if f.endswith('.obf'):
                obffile = f
        return self.work_dir + '/' + obffile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Converts OSM PBF to OSMAnd OBF Format.")
    parser.add_argument('-p', '--pbf-file', required=True,
                        dest="pbffile", help='The PBF file to convert')
    parser.add_argument('-w', '--work-dir', required=True,
                        dest="work_dir", help='The path to the working directory')
    parser.add_argument('-m', '--map-creator-dir', required=True,
                        dest="map_creator_dir", help="The path to the OsmAndMapCreator directory")
    parser.add_argument('-d', '--debug', action="store_true", help="Turn on debug output")
    args = parser.parse_args()
    config = {}
    for k, v in vars(args).items():
        if (v == None):
            continue
        else:
            config[k] = v
    pbffile = config.get('pbffile')
    work_dir = config.get('work_dir')
    map_creator_dir = config.get('map_creator_dir')
    debug = False
    if config.get('debug'):
        debug = True
    OSMToOBF(
        pbffile=pbffile, work_dir=work_dir,
        map_creator_dir=map_creator_dir, debug=debug
    )
