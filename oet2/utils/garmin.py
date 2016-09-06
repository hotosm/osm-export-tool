# -*- coding: utf-8 -*-
import argparse
import logging
import os
import subprocess
from string import Template
from StringIO import StringIO

from lxml import etree

logger = logging.getLogger(__name__)


class GarminConfigParser(object):
    """
    Parse the conf/garmin_config.xml file.
    """

    def __init__(self, config=None):
        """
        Initialize the parser with the config file.
        """
        self.config = config

    def get_config(self, ):
        params = {}
        f = open(self.config)
        xml = f.read()
        tree = etree.parse(StringIO(xml))
        mkgmap_ele = tree.xpath('//mkgmap')
        splitter_ele = tree.xpath('//splitter')
        xmx_ele = tree.xpath('//xmx')
        desc_ele = tree.xpath('//description')
        family_name_ele = tree.xpath('//family-name')
        family_id_ele = tree.xpath('//family-id')
        series_ele = tree.xpath('//series-name')
        assert len(mkgmap_ele) == 1, "No 'mkgmap' element found in {0}.".format(self.config)
        assert len(splitter_ele) == 1, "No 'splitter' element found in {0}.".format(self.config)
        assert len(xmx_ele) == 1, "No 'xmx' element found in {0}.".format(self.config)
        assert len(desc_ele) == 1, "No 'description' element found in {0}.".format(self.config)
        assert len(family_name_ele) == 1, "No 'family-name' element found in {0}.".format(self.config)
        assert len(family_id_ele) == 1, "No 'family-id' element found in {0}.".format(self.config)
        assert len(series_ele) == 1, "No 'series-name' element found in {0}.".format(self.config)
        mkgmap = mkgmap_ele[0].text
        splitter = splitter_ele[0].text
        xmx = xmx_ele[0].text
        description = desc_ele[0].text
        family_name = family_name_ele[0].text
        family_id = family_id_ele[0].text
        series_name = series_ele[0].text
        params['mkgmap'] = mkgmap
        params['splitter'] = splitter
        params['xmx'] = xmx
        params['description'] = description
        params['family_name'] = family_name
        params['family_id'] = family_id
        params['series_name'] = series_name
        return params


class OSMToIMG(object):
    """
    Converts PBF to Garmin IMG format.

    Splits pbf into smaller tiles, generates .img files for each split,
    then patches the .img files back into a single .img file
    suitable for deployment to a Garmin GPS unit.
    """

    def __init__(self, pbffile=None, work_dir=None, config=None,
                 region=None, zipped=True, debug=False):
        # the pbf file to convert to garmin
        self.pbffile = pbffile
        if not os.path.exists(self.pbffile):
            raise IOError('Cannot find PBF file for this task.')
        self.work_dir = work_dir
        self.config = config
        self.region = region
        self.zipped = zipped
        self.debug = debug
        config_parser = GarminConfigParser(self.config)
        self.params = config_parser.get_config()

        # command template for the splitter.jar utility
        self.splitter_cmd = Template("""
            java -Xmx$xmx -jar $splitter \
            --output-dir=$work_dir \
            $pbffile""")

        # command template for the mkgmap.jar utility
        self.mkgmap_cmd = Template("""
            java -Xmx$xmx -jar $mkgmap \
            --gmapsupp \
            --output-dir=$work_dir \
            --description="$description" \
            --mapname=80000111 \
            --family-name="$family_name" \
            --family-id="$family_id" \
            --series-name="$series_name" \
            --region-name="$region" \
            --index \
            --route \
            --generate-sea=extend-sea-sectors \
            --draw-priority=100 \
            --read-config=$templateargs
        """)
        self.zip_cmd = Template("zip -j $zipfile $imgfile")
        self.imgfile = self.work_dir + '/gmapsupp.img'

    def run_splitter(self, ):
        """
        Run the splitter utility to split large pbf into smaller tiles.
        """
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir, 6600)
        # get the configuration params
        splitter = self.params.get('splitter')
        xmx = self.params.get('xmx')

        # run the pbf splitter
        splitter_cmd = self.splitter_cmd.safe_substitute(
            {'xmx': xmx, 'splitter': splitter,
             'work_dir': self.work_dir, 'pbffile': self.pbffile}
        )
        if(self.debug):
            print 'Running: %s' % splitter_cmd
        proc = subprocess.Popen(splitter_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, " {0} process failed with returncode: {1}".format(splitter, returncode)
        if self.debug:
            print 'splitter returned: %s' % returncode

    def run_mkgmap(self,):
        """
        Generate the IMG file.
        """
        # get the template.args file created by splitter
        # see: http://wiki.openstreetmap.org/wiki/Mkgmap/help/splitter
        templateargs = self.work_dir + '/template.args'
        assert os.path.exists(templateargs), "No 'template.args' file found in {0}".format(self.work_dir)
        # pull out required config
        mkgmap = self.params.get('mkgmap')
        xmx = self.params.get('xmx')
        description = self.params.get('description')
        family_name = self.params.get('family_name')
        family_id = self.params.get('family_id')
        series_name = self.params.get('series_name')
        # run mkgmap to generate the .img file
        mkgmap_cmd = self.mkgmap_cmd.safe_substitute(
            {'xmx': xmx, 'mkgmap': mkgmap, 'work_dir': self.work_dir,
             'description': description, 'family_name': family_name,
             'family_id': family_id, 'series_name': series_name,
             'region': self.region, 'templateargs': templateargs}
        )
        if(self.debug):
            print 'Running: %s' % mkgmap_cmd
        proc = subprocess.Popen(mkgmap_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, " {0} process failed with returncode: {1}".format(mkgmap, returncode)
        if self.debug:
            print 'mkgmap returned: %s' % returncode
        # return the path to the img file
        if self.zipped and returncode == 0:
            img_zipped = self._zip_img_file()
            return img_zipped
        else:
            return self.imgfile

    def _zip_img_file(self, ):
        img_zipped = self.work_dir + '/garmin.zip'
        zip_cmd = self.zip_cmd.safe_substitute({'zipfile': img_zipped,
                                                'imgfile': self.imgfile})
        proc = subprocess.Popen(zip_cmd, shell=True, executable='/bin/bash',
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if returncode != 0:
            logger.error('%s', stderr)
            raise Exception, 'Failed to create zipfile for {0}'.format(self.kmlfile)
        if returncode == 0:
            # remove the img file
            os.remove(self.imgfile)
        if self.debug:
            print 'Zipped Garmin IMG: {0}'.format(img_zipped)
        return img_zipped


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Converts OSM PBF to Garmin IMG Format.")
    parser.add_argument('-p', '--pbf-file', required=True,
                        dest="pbffile", help='The PBF file to convert')
    parser.add_argument('-w', '--work-dir', required=True,
                        dest="work_dir", help='The path to the working directory')
    parser.add_argument('-c', '--config-file', required=True,
                        dest="config", help='The path to the garmin config file')
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
    map_creator_dir = config.get('config')
    debug = False
    if config.get('debug'):
        debug = True
    OSMToIMG(
        pbffile=pbffile, work_dir=work_dir,
        config=config, debug=debug)
