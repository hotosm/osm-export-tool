from __future__ import absolute_import

import os
import shutil
import zipfile

from .artifact import Artifact
from .garmin_img import GarminIMG
from .geopackage import Geopackage
from .kml import KML
from .mbtiles import MBTiles
from .mwm import MWM
from .osm_pbf import OSM_PBF
from .osm_xml import OSM_XML
from .osmand_obf import OsmAndOBF
from .shp import Shapefile


class Zipper(object):
    """
    Utility class to handle renaming, zipping and moving files to storage in
    one place.
    """

    def __init__(self, job_name, stage_dir, target_dir, boundary_geom,
                 feature_selection):
        self.job_name = job_name
        self.stage_dir = stage_dir
        self.target_dir = target_dir
        self.boundary_geom = boundary_geom
        self.feature_selection = feature_selection
        self._zipped_resources = []

    def run(self, results_list):
        zips = []
        for a in results_list:
            # the created zipfile must end with only .zip for the HDX
            # geopreview to work
            zipfile_name = self.job_name + "_" + os.path.basename(
                a.basename).replace('.', '_') + ".zip"
            zipfile_path = os.path.join(self.stage_dir,
                                        zipfile_name).encode('utf-8')
            with zipfile.ZipFile(zipfile_path, 'w', zipfile.ZIP_DEFLATED, True) as z:
                for filename in a.parts:
                    z.write(filename,
                            self.job_name + "_" + os.path.basename(filename))
                if a.theme:
                    z.writestr("README.txt",
                               self.feature_selection.zip_readme(a.theme))
                z.writestr("clipping_boundary.geojson",
                           self.boundary_geom.json)
            target_path = os.path.join(self.target_dir,
                                       zipfile_name).encode('utf-8')
            shutil.move(zipfile_path, target_path)
            zips.append(target_path)

            # side effect
            self._zipped_resources.append(
                Artifact(
                    [os.path.basename(target_path)],
                    a.format_name,
                    theme=a.theme))
        return zips

    @property
    def zipped_resources(self):
        return self._zipped_resources


class RunManager(object):
    prereqs = {
        OSM_XML: None,
        OSM_PBF: OSM_XML,
        Geopackage: OSM_PBF,
        Shapefile: Geopackage,
        KML: Geopackage,
        OsmAndOBF: OSM_PBF,
        GarminIMG: OSM_PBF,
        MBTiles: None,
        MWM: OSM_PBF,
    }

    def __init__(self,
                 formats,
                 aoi_geom,
                 feature_selection,
                 stage_dir,
                 map_creator_dir=None,
                 garmin_splitter=None,
                 garmin_mkgmap=None,
                 overpass_api_url=None,
                 per_theme=False,
                 on_task_start=lambda formatcls: None,
                 on_task_success=lambda formatcls, results: None,
                 mbtiles_maxzoom=None,
                 mbtiles_minzoom=None,
                 mbtiles_source=None):

        self.formats = formats
        self.aoi_geom = aoi_geom
        self.dir = stage_dir
        self.feature_selection = feature_selection
        self.garmin_splitter = garmin_splitter
        self.garmin_mkgmap = garmin_mkgmap
        self.map_creator_dir = map_creator_dir
        self.overpass_api_url = overpass_api_url
        self.per_theme = per_theme
        self.on_task_start = on_task_start
        self.on_task_success = on_task_success
        self.mbtiles_maxzoom = mbtiles_maxzoom
        self.mbtiles_minzoom = mbtiles_minzoom
        self.mbtiles_source = mbtiles_source
        self.results = {}

    def run_format(self, formatcls):
        if formatcls in self.results:
            return
        prereq = RunManager.prereqs[formatcls]
        if prereq and prereq not in self.results:
            self.run_format(prereq)

        if formatcls == OSM_XML:
            task = OSM_XML(
                self.aoi_geom,
                os.path.join(self.dir, 'export.osm'),
                url=self.overpass_api_url)

        if formatcls == OSM_PBF:
            task = OSM_PBF(
                os.path.join(self.dir, 'export.osm'),
                os.path.join(self.dir, 'export.pbf'))

        if formatcls == Geopackage:
            task = Geopackage(
                os.path.join(self.dir, 'export.pbf'),
                os.path.join(self.dir, 'export.gpkg'),
                self.dir,
                self.feature_selection,
                self.aoi_geom,
                per_theme=self.per_theme)

        if formatcls == GarminIMG:
            assert self.garmin_splitter and self.garmin_mkgmap
            task = GarminIMG(
                os.path.join(self.dir, 'export.pbf'), self.dir,
                self.garmin_splitter, self.garmin_mkgmap, self.aoi_geom)

        if formatcls == OsmAndOBF:
            assert self.map_creator_dir
            task = OsmAndOBF(
                os.path.join(self.dir, 'export.pbf'), self.dir,
                self.map_creator_dir)

        if formatcls == KML:
            task = KML(
                os.path.join(self.dir, 'export.gpkg'),
                self.dir,
                self.feature_selection,
                per_theme=self.per_theme)

        if formatcls == Shapefile:
            task = Shapefile(
                os.path.join(self.dir, 'export.gpkg'),
                self.dir,
                self.feature_selection,
                per_theme=self.per_theme)

        if formatcls == MWM:
            task = MWM(os.path.join(self.dir, 'export.pbf'))

        if formatcls == MBTiles:
            extent = self.aoi_geom.extent
            west = max(extent[0], -180)
            south = max(extent[1], -90)
            east = min(extent[2], 180)
            north = min(extent[3], 90)
            task = MBTiles(os.path.join(self.dir, 'export.mbtiles'), (west, south, east, north), self.mbtiles_source, self.mbtiles_minzoom, self.mbtiles_maxzoom)

        self.on_task_start(formatcls)
        task.run()
        self.on_task_success(formatcls, task.results)
        self.results[formatcls] = task

    def run(self):
        for formatcls in self.formats:
            self.run_format(formatcls)


if __name__ == '__main__':
    from feature_selection.feature_selection import FeatureSelection
    import logging
    from django.contrib.gis.geos import GEOSGeometry
    from simplify import simplify_geom

    logging.basicConfig(level=logging.DEBUG)
    feature_selection = FeatureSelection.example('hdx')
    stage_dir = 'scratch/'
    try:
        os.makedirs('scratch', 6600)
    except Exception:
        pass
    aoi_geom = GEOSGeometry(
        open('../hdx_exports/adm0/SEN_adm0.geojson').read())
    aoi_geom = simplify_geom(aoi_geom)

    # aoi_geom = Polygon.from_bbox((-10.80029,6.3254236,-10.79809,6.32752))
    aoi_geom = GEOSGeometry(
        'POLYGON((-17.4682611807514 14.7168486569183,-17.4682611807514 \
        14.6916060414416,-17.4359733230442 14.6916060414416,-17.4359733230442 \
        14.7168486569183,-17.4682611807514 14.7168486569183))')
    fmts = [OSM_XML, OSM_PBF, Geopackage, Shapefile, KML, GarminIMG, OsmAndOBF]
    r = RunManager(
        fmts,
        aoi_geom,
        feature_selection,
        stage_dir,
        map_creator_dir='../../OsmAndMapCreator-main',
        garmin_splitter='../../splitter-r583/splitter.jar',
        garmin_mkgmap='../../mkgmap-r3890/mkgmap.jar',
        per_theme=False,
        overpass_api_url=os.environ['OVERPASS_API_URL'])
    r.run()

    zipper = Zipper("test", stage_dir, "target", aoi_geom, feature_selection)
    for f in fmts:
        zipper.run(r.results[f].results)
    print zipper.zipped_resources
