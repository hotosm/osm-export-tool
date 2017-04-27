# -*- coding: utf-8 -*-
import logging
import subprocess
import zipfile

from artifact import Artifact

LOG = logging.getLogger(__name__)

def geos_to_poly(aoi,fname):
    with open(fname,'w') as f:
        f.write("export_bounds\n")
        f.write("1\n")
        for coord in aoi.coords[0]:
            f.write("%f %f\n" % (coord[0],coord[1]))
        f.write("END\n")
        f.write("END")

class GarminIMG(object):
    """
    Converts PBF to Garmin IMG format.

    Splits pbf into smaller tiles, generates .img files for each split,
    then patches the .img files back into a single .img file
    suitable for deployment to a Garmin GPS unit.
    """
    name = "garmin_img"
    description = "Garmin IMG"


    def __init__(self, input_pbf, work_dir, splitter, mkgmap, aoi_geom):
        # the pbf file to convert to garmin
        self.input_pbf = input_pbf
        self.work_dir = work_dir
        self.splitter = splitter
        self.mkgmap = mkgmap
        self.aoi_geom = aoi_geom

    def run(self):
        # Run the splitter utility to split large pbf into smaller tiles.
        polygon_file = self.work_dir + "/bounds.poly"
        geos_to_poly(self.aoi_geom,polygon_file)

        splitter_cmd = "java -Xmx1024m -jar {splitter} --polygon-file={polygon_file} --output-dir={work_dir} {pbffile}"
        cmd = splitter_cmd.format(splitter=self.splitter,work_dir=self.work_dir,pbffile=self.input_pbf,polygon_file=polygon_file)
        LOG.debug('Running: %s' % cmd)
        subprocess.check_call(cmd, shell=True, executable='/bin/bash')
        # Generate the IMG file.
        # get the template.args file created by splitter
        # see: http://wiki.openstreetmap.org/wiki/Mkgmap/help/splitter
        mkgmap_cmd = """
            java \
            -Xmx1024m \
            -jar {mkgmap} \
            --gmapsupp \
            --output-dir={work_dir} \
            --description="HOT Export Garmin Map" \
            --mapname=80000111 \
            --family-name="HOT Exports" \
            --family-id="2" \
            --series-name="HOT Exports" \
            --index \
            --route \
            --generate-sea=extend-sea-sectors \
            --draw-priority=100 \
            --read-config={work_dir}/template.args \
        """
        cmd = mkgmap_cmd.format(mkgmap=self.mkgmap,work_dir=self.work_dir)
        LOG.debug('Running: %s' % cmd)
        subprocess.check_call(cmd, shell=True, executable='/bin/bash')

    @property
    def results(self):
        return [Artifact([self.work_dir+"/gmapsupp.img"],GarminIMG.name)]
