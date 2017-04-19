from osm_xml import OSM_XML
from osm_pbf import OSM_PBF
from kml import KML
from geopackage import Geopackage
from shp import Shapefile
from theme_gpkg import ThematicGPKG
from theme_shp import ThematicSHP
from garmin_img import GarminIMG
from osmand_obf import OsmAndOBF

class RunManager(object):
    prereqs = {
        OSM_XML: None,
        OSM_PBF: OSM_XML,
        Geopackage: OSM_PBF,
        Shapefile: Geopackage,
        KML: Geopackage,
        ThematicGPKG: Geopackage,
        ThematicSHP: ThematicGPKG,
        OsmAndOBF: OSM_PBF,
        GarminIMG: OSM_PBF
    }

    def __init__(
        self,
        formats,
        aoi_geom,
        feature_selection,
        stage_dir,
        map_creator_dir=None,
        garmin_splitter=None,
        garmin_mkgmap=None,
        per_theme=False,
        on_task_start=lambda formatcls :None,
        on_task_success=lambda formatcls,results:None):

        self.formats = formats
        self.aoi_geom = aoi_geom
        self.dir = stage_dir
        self.feature_selection = feature_selection
        self.garmin_splitter=garmin_splitter
        self.garmin_mkgmap = garmin_mkgmap
        self.map_creator_dir = map_creator_dir
        self.per_theme = per_theme
        self.on_task_start=on_task_start
        self.on_task_success=on_task_success
        self.results = {}

    def run_format(self,formatcls):
        if formatcls in self.results:
            return
        prereq = RunManager.prereqs[formatcls]
        if prereq and prereq not in self.results:
            self.run_format(prereq)

        if formatcls == OSM_XML:
            task = OSM_XML(self.aoi_geom, self.dir + 'osm_xml.osm')
        if formatcls == OSM_PBF:
            task = OSM_PBF(self.dir + 'osm_xml.osm',self.dir+'osm_pbf.pbf')
        if formatcls == Geopackage:
            task = Geopackage(
                self.dir+'osm_pbf.pbf',
                self.dir+'geopackage.gpkg',
                self.dir,
                self.feature_selection,
                self.aoi_geom
            )
        if formatcls == GarminIMG:
            assert self.garmin_splitter and self.garmin_mkgmap
            task = GarminIMG(
                    self.dir+'osm_pbf.pbf',
                    self.dir+'garmin_img.zip',
                    self.dir,
                    self.garmin_splitter,
                    self.garmin_mkgmap)
        if formatcls == OsmAndOBF:
            assert self.map_creator_dir
            task = OsmAndOBF(self.dir+'osm_pbf.pbf',self.dir,self.map_creator_dir)
        if formatcls == KML:
            task = KML(self.dir + 'geopackage.gpkg',self.dir + 'kml.kmz')
        if formatcls == Shapefile:
            task = Shapefile(self.dir + 'geopackage.gpkg',self.dir+'shapefile.shp.zip')
        if formatcls == ThematicGPKG:
            task = ThematicGPKG(self.dir+'geopackage.gpkg',self.feature_selection,self.dir,per_theme=self.per_theme)
        if formatcls == ThematicSHP:
            task = ThematicSHP(self.dir+'geopackage.gpkg',self.dir+'thematic_shps',self.feature_selection,self.aoi_geom,per_theme=self.per_theme)

        self.on_task_start(formatcls)
        task.run()
        self.on_task_success(formatcls,task.results)
        self.results[formatcls] = task

    def run(self):
        for formatcls in self.formats:
            self.run_format(formatcls)

if __name__ == '__main__':
    from feature_selection.feature_selection import FeatureSelection
    import os
    import logging
    from django.contrib.gis.geos import GEOSGeometry, Polygon
    logging.basicConfig(level=logging.DEBUG)
    feature_selection = FeatureSelection.example('hdx')
    stage_dir = 'scratch/'
    try:
        os.makedirs('scratch', 6600)
    except:
        pass
    #aoi_geom = GEOSGeometry(open('../hdx_exports/adm0/SEN_adm0.geojson').read())
    #aoi_geom = Polygon.from_bbox((-10.80029,6.3254236,-10.79809,6.32752))
    #aoi_geom = aoi_geom.buffer(0.02)
    #aoi_geom = aoi_geom.simplify(0.01)
    # TODO Shapefiles (non-thematic) broken
    aoi_geom = GEOSGeometry('POLYGON((-17.4682611807514 14.7168486569183,-17.4682611807514 14.6916060414416,-17.4359733230442 14.6916060414416,-17.4359733230442 14.7168486569183,-17.4682611807514 14.7168486569183))')
    r = RunManager(
        [OSM_XML,OSM_PBF,Geopackage,KML,ThematicGPKG,ThematicSHP,GarminIMG,OsmAndOBF],
        aoi_geom,
        feature_selection,
        stage_dir,
        map_creator_dir='../../OsmAndMapCreator-main',
        garmin_splitter='../../splitter-r583/splitter.jar',
        garmin_mkgmap='../../mkgmap-r3890/mkgmap.jar',
        per_theme=True
    )
    r.run()
