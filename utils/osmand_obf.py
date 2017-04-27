# -*- coding: utf-8 -*-
import logging
import os
import subprocess

from artifact import Artifact

LOG = logging.getLogger(__name__)

BATCH_XML = """<?xml version="1.0" encoding="utf-8"?>
<!--
    OsmAnd Batch Creation Config Template.
    Determines where the OBF creation process is staged
    and configures the export process.
-->
<batch_process>
	<process_attributes mapZooms="" renderingTypesFile="" zoomWaySmoothness=""
		osmDbDialect="sqlite" mapDbDialect="sqlite"/>
	 <!-- zoomWaySmoothness - 1-4, typical mapZooms - 11;12;13-14;15-   -->
	<process directory_for_osm_files="{work_dir}/osmand"
             directory_for_index_files="{work_dir}"
             directory_for_generation="{work_dir}"
             skipExistingIndexesAt="{work_dir}"
             indexPOI="true"
             indexRouting="true"
             indexMap="true"
             indexTransport="true"
             indexAddress="true">
	</process>
</batch_process>
"""

OBF_CMD = """
java -Djava.util.logging.config.file=logging.properties \
-Xms256M -Xmx1024M -cp "{map_creator_dir}/OsmAndMapCreator.jar:{map_creator_dir}/lib/OsmAnd-core.jar:{map_creator_dir}/lib/*.jar" \
net.osmand.data.index.IndexBatchCreator {batch_xml}
"""

class OsmAndOBF(object):
    """
    Convert osm input to obf output.
    """
    name = "osmand_obf"
    description = 'OsmAnd OBF'

    def __init__(self,input_pbf,work_dir,map_creator_dir):
        """
        Initialize the OSMToOBF utility.

        Args:
            work_dir: the staging dir for the conversion process
            map_creator_dir: the location of the osmand map creator utility
        """
        self.input_pbf = input_pbf
        self.work_dir = work_dir
        self.map_creator_dir = map_creator_dir

    def run(self):
        """
        Perform the conversion from PBF to OBF.
        """
        try:
            os.makedirs(self.work_dir + "/osmand")
        except:
            pass
        try:
            os.link(self.input_pbf,self.work_dir+"/osmand/osmand.osm.pbf")
        except:
            pass
        with open(self.work_dir + "/batch.xml",'w') as batch_xml:
            batch_xml.write(BATCH_XML.format(work_dir=self.work_dir))
        cmd = OBF_CMD.format(map_creator_dir=self.map_creator_dir,batch_xml=self.work_dir + "/batch.xml")
        LOG.debug('Running: %s' % cmd)
        proc = subprocess.check_call(cmd, shell=True, executable='/bin/bash')

    @property
    def results(self):
        return [Artifact([self.work_dir + "/Osmand_2.obf"],OsmAndOBF.name)]
