-- create planet_osm_line
-- add spatial metadata
-- drop the old line table
CREATE TABLE planet_osm_point AS SELECT * FROM points;
DROP TABLE points;
UPDATE gpkg_contents SET table_name = "planet_osm_point",identifier = "planet_osm_point" WHERE table_name = "points";
UPDATE gpkg_geometry_columns SET table_name = "planet_osm_point" WHERE table_name = "points";
-- create planet_osm_line
-- add spatial metadata
-- drop the old line table
CREATE TABLE planet_osm_line AS SELECT * FROM lines;
DROP TABLE lines;
UPDATE gpkg_contents SET table_name = "planet_osm_line",identifier = "planet_osm_line" WHERE table_name = "lines";
UPDATE gpkg_geometry_columns SET table_name = "planet_osm_line" WHERE table_name = "lines";
-- create planet_osm_line
-- add spatial metadata
-- drop the old line table
CREATE TABLE planet_osm_polygon AS SELECT * FROM multipolygons;
DROP TABLE multipolygons;
UPDATE gpkg_contents SET table_name = "planet_osm_polygon", identifier = "planet_osm_polygon" WHERE table_name = "multipolygons";
UPDATE gpkg_geometry_columns SET table_name = "planet_osm_polygon" WHERE table_name = "multipolygons";
-- drop other tables created by ogr -- for now!
-- should see if these features can be recovered
DROP TABLE multilinestrings;
DROP TABLE other_relations;
DELETE FROM gpkg_contents WHERE table_name="multilinestrings";
DELETE FROM gpkg_geometry_columns WHERE table_name="multilinestrings";
DELETE FROM gpkg_contents WHERE table_name="other_relations";
DELETE FROM gpkg_geometry_columns WHERE table_name="other_relations";
DELETE FROM gpkg_extensions WHERE table_name is not NULL;

-- add z_index columns
ALTER TABLE planet_osm_point ADD COLUMN z_index INTEGER(4) DEFAULT 0;
ALTER TABLE planet_osm_line ADD COLUMN z_index INTEGER(4) DEFAULT 0;
ALTER TABLE planet_osm_polygon ADD COLUMN z_index INTEGER(4) DEFAULT 0;
