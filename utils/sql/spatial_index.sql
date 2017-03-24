UPDATE 'planet_osm_point' SET geom=GeomFromGPB(geom);
UPDATE 'planet_osm_line' SET geom=GeomFromGPB(geom);
UPDATE 'planet_osm_polygon' SET geom=GeomFromGPB(geom);

SELECT gpkgAddSpatialIndex('planet_osm_point', 'geom');
SELECT gpkgAddSpatialIndex('planet_osm_line', 'geom');
SELECT gpkgAddSpatialIndex('planet_osm_polygon', 'geom');

UPDATE 'planet_osm_point' SET geom=AsGPB(geom);
UPDATE 'planet_osm_line' SET geom=AsGPB(geom);
UPDATE 'planet_osm_polygon' SET geom=AsGPB(geom);

DROP TABLE rtree_lines_geom;
DROP TABLE rtree_multilinestrings_geom;
DROP TABLE rtree_multipolygons_geom;
DROP TABLE rtree_other_relations_geom;
DROP TABLE rtree_points_geom;
