-- create planet_osm_line
-- add spatial metadata
-- drop the old line table
CREATE TABLE planet_osm_point AS SELECT * FROM points;
SELECT RecoverGeometryColumn('planet_osm_point','Geometry',4326, 'POINT');
SELECT CreateSpatialIndex('planet_osm_point', 'Geometry');
.dropgeo points

VACUUM;

-- create planet_osm_line
-- add spatial metadata
-- drop the old line table
CREATE TABLE planet_osm_line AS SELECT * FROM lines;
SELECT RecoverGeometryColumn('planet_osm_line','Geometry',4326, 'LINESTRING');
SELECT CreateSpatialIndex('planet_osm_line', 'Geometry');
.dropgeo lines

VACUUM;

-- create planet_osm_line
-- add spatial metadata
-- drop the old line table
CREATE TABLE planet_osm_polygon AS SELECT * FROM multipolygons;
SELECT RecoverGeometryColumn('planet_osm_polygon','Geometry',4326, 'MULTIPOLYGON');
SELECT CreateSpatialIndex('planet_osm_polygon', 'Geometry');
.dropgeo multipolygons

-- add z_index columns

ALTER TABLE planet_osm_point ADD COLUMN z_index INTEGER(4) DEFAULT 0;
ALTER TABLE planet_osm_line ADD COLUMN z_index INTEGER(4) DEFAULT 0;
ALTER TABLE planet_osm_polygon ADD COLUMN z_index INTEGER(4) DEFAULT 0;

-- drop other tables created by ogr -- for now!
-- should see if these features can be recovered
.dropgeo multilinestrings
.dropgeo other_relations

VACUUM;





