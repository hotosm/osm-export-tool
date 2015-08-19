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

-- create the planet_osm_roads table

CREATE TABLE planet_osm_roads (
    OGC_FID INTEGER NOT NULL PRIMARY KEY,
    osm_id INTEGER(11) NOT NULL,
    z_index INTEGER(4),
    railway VARCHAR(255),
    highway VARCHAR(255),
    boundary VARCHAR(255)
);

SELECT AddGeometryColumn('planet_osm_roads','Geometry',4326, 'LINESTRING');
SELECT CreateSpatialIndex('planet_osm_roads', 'Geometry');

-- populate the planet_osm_roads table

INSERT INTO planet_osm_roads (Geometry, osm_id, z_index, highway) 
    SELECT Geometry, osm_id, z_index, highway FROM planet_osm_line WHERE highway IN 
    ('motorway_link', 'motorway', 'trunk_link', 'trunk', 'primary_link', 'primary', 'secondary_link', 'secondary');
    
INSERT INTO planet_osm_roads (Geometry, osm_id, z_index, railway) 
                    SELECT Geometry, osm_id, z_index, railway FROM planet_osm_line WHERE railway <> '';

INSERT INTO planet_osm_roads (Geometry, osm_id, z_index, boundary) 
                        SELECT Geometry, osm_id, z_index, boundary FROM planet_osm_line WHERE boundary <> '';
                        

-- drop other tables created by ogr -- for now!
-- should see if these features can be recovered
.dropgeo multilinestrings
.dropgeo other_relations

VACUUM;





