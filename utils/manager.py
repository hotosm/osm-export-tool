from osm_xml import OSM_XML
from osm_pbf import OSM_PBF
from kml import KML
from geopackage import Geopackage
from shp import Shapefile
from garmin_img import GarminIMG
from osmand_obf import OsmAndOBF

import os
import json
import shutil
import zipfile

def simplify_max_points(input_geom,max_points=500):
    geom = input_geom
    num_coords = geom.num_coords
    param = 0.01
    while num_coords > 500:
        geom = geom.simplify(param,preserve_topology=True)
        param = param * 2
        num_coords = geom.num_coords
    return geom

# ugly class to handle renaming, zipping and moving
class Zipper(object):
    def __init__(self,job_name,stage_dir,target_dir,boundary_geom):
        self.job_name = job_name
        self.stage_dir = stage_dir
        self.target_dir = target_dir
        self.boundary_geom = boundary_geom
        self.boundary_path = os.path.join(self.stage_dir,'boundary.geojson')
        with open(self.boundary_path,'w') as b:
            b.write(json.dumps(self.boundary_geom.json))

        self._resources_by_theme = {}

    def run(self,results_dict,resource_type):
        # hack, for themeless export types (XML, PBF, IMG, OBF)
        if isinstance(results_dict,list):
            retval = []
            for item in results_dict:
                basename = os.path.basename(item)
                target_path = os.path.join(self.target_dir,basename)
                shutil.copy(item,target_path)
                retval.append(target_path)
            return retval

        zips = []
        for theme, groups in results_dict.iteritems():
            for group in groups:
                # the created zipfile must end with only .zip for the HDX geopreview to work
                zipfile_name = self.job_name + "_" + os.path.basename(group[0]).replace('.','_') + ".zip"
                zipfile_path = os.path.join(self.stage_dir,zipfile_name)
                with zipfile.ZipFile(zipfile_path,'w',zipfile.ZIP_DEFLATED) as z:
                    for filename in group:
                        z.write(filename,self.job_name + "_" + os.path.basename(filename))
                    z.write(self.boundary_path,"boundary.geojson")
                target_path = os.path.join(self.target_dir,zipfile_name)
                shutil.move(zipfile_path,target_path)
                zips.append(target_path)

                # side effect
                if theme not in self._resources_by_theme:
                    self._resources_by_theme[theme] = []
                self._resources_by_theme[theme].append((zipfile_name,resource_type))
        return zips

    def resources_by_theme(self):
        return self._resources_by_theme


class RunManager(object):
    prereqs = {
        OSM_XML: None,
        OSM_PBF: OSM_XML,
        Geopackage: OSM_PBF,
        Shapefile: Geopackage,
        KML: Geopackage,
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
            task = OSM_XML(self.aoi_geom, self.dir + 'export.osm')
        if formatcls == OSM_PBF:
            task = OSM_PBF(self.dir + 'export.osm',self.dir+'export.pbf')
        if formatcls == Geopackage:
            task = Geopackage(
                self.dir+'export.pbf',
                self.dir+'export.gpkg',
                self.dir,
                self.feature_selection,
                self.aoi_geom,
                per_theme=self.per_theme
            )
        if formatcls == GarminIMG:
            assert self.garmin_splitter and self.garmin_mkgmap
            task = GarminIMG(
                    self.dir+'export.pbf',
                    self.dir,
                    self.garmin_splitter,
                    self.garmin_mkgmap)
        if formatcls == OsmAndOBF:
            assert self.map_creator_dir
            task = OsmAndOBF(self.dir+'export.pbf',self.dir,self.map_creator_dir)
        if formatcls == KML:
            task = KML(self.dir + 'export.gpkg',self.dir,self.feature_selection)
        if formatcls == Shapefile:
            task = Shapefile(self.dir + 'export.gpkg',self.dir,self.feature_selection)

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
    aoi_geom = GEOSGeometry(open('../hdx_exports/adm0/SEN_adm0.geojson').read())
    aoi_geom = simplify_max_points(aoi_geom,500)
    
    #aoi_geom = Polygon.from_bbox((-10.80029,6.3254236,-10.79809,6.32752))
    #aoi_geom = aoi_geom.buffer(0.02)
    #aoi_geom = aoi_geom.simplify(0.01)
    aoi_geom = GEOSGeometry('POLYGON((-17.4682611807514 14.7168486569183,-17.4682611807514 14.6916060414416,-17.4359733230442 14.6916060414416,-17.4359733230442 14.7168486569183,-17.4682611807514 14.7168486569183))')
    fmts = [Geopackage,Shapefile,KML,OsmAndOBF,GarminIMG,OSM_XML,OSM_PBF]
    r = RunManager(
        fmts,
        aoi_geom,
        feature_selection,
        stage_dir,
        map_creator_dir='../../OsmAndMapCreator-main',
        garmin_splitter='../../splitter-r583/splitter.jar',
        garmin_mkgmap='../../mkgmap-r3890/mkgmap.jar',
        per_theme=True
    )
    r.run()

    zipper = Zipper("test",stage_dir,"target",aoi_geom)
    for f in fmts:
        zipper.run(r.results[f].results,f.name)

    print zipper.resources_by_theme()
