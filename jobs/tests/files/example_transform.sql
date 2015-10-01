--renommage des tables
ALTER TABLE planet_osm_point RENAME TO old_planet_osm_point;
ALTER TABLE planet_osm_line  RENAME TO old_planet_osm_line;
ALTER TABLE planet_osm_polygon  RENAME TO old_planet_osm_polygon ;

--creation des nouvelles tables avec colonnes en Francais
--creation de la table point
CREATE TABLE planet_osm_point(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				acces VARCHAR (80),
				artificiel VARCHAR (80),
				artisanat VARCHAR (80),
				bati VARCHAR (80),
				bureau VARCHAR (80),
				commerce VARCHAR (80),
				energie VARCHAR (80),
				equipement VARCHAR (80),
				gue VARCHAR (80),
				histoire VARCHAR (80),
				hydrograph VARCHAR (80),
				lieu VARCHAR (80),
				loisir VARCHAR (80),
				marais VARCHAR (80),
				nature VARCHAR (80),
				nom VARCHAR (80),
				obstacle VARCHAR (80),
				osm_id VARCHAR (80),
				piste VARCHAR (80),
				pont VARCHAR (80),
				religion VARCHAR (80),
				revetement VARCHAR (80),
				sensunique VARCHAR (80),
				sport VARCHAR (80),
				tourisme VARCHAR (80),
				velo VARCHAR (80),
				voie VARCHAR (80)
				);

--creation de la colonne spatiale dans la table point
SELECT AddGeometryColumn('planet_osm_point', 'the_geom', 3857, 'POINT', 'XY');

--copie des donnÃƒÂ©es de la table source renommÃƒÂ©e dans la nouvelle
INSERT INTO planet_osm_point (
				the_geom,
				acces,
				artificiel,
				artisanat,
				bati,
				bureau,
				commerce,
				energie,
				equipement,
				gue,
				histoire,
				hydrograph,
				lieu,
				loisir,
				marais,
				nature,
				nom,
				obstacle,
				osm_id,
				piste,
				pont,
				religion,
				revetement,
				sensunique,
				sport,
				tourisme,
				velo,
				voie
				)

SELECT
		  		Geometry,
				access,
				man_made,
				craft,
				building,
				office,
				shop,
				power,
				amenity,
				ford,
				historic,
				waterway,
				place,
				leisure,
				wetland,
				natural,
				name,
				barrier,
				osm_id,
				aeroway,
				bridge,
				religion,
				surface,
				oneway,
				sport,
				tourism,
				bicycle,
				highway

FROM old_planet_osm_point ;

CREATE TABLE planet_osm_line (
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				acces VARCHAR (80),
				artificiel VARCHAR (80),
				bati VARCHAR (80),
				energie VARCHAR (80),
				equipement VARCHAR (80),
				gue VARCHAR (80),
				loisir VARCHAR (80),
				nature VARCHAR (80),
				nom VARCHAR (80),
				obstacle VARCHAR (80),
				osm_id VARCHAR (80),
				pont VARCHAR (80),
				revetement VARCHAR (80),
				sensunique VARCHAR (80),
				tourisme VARCHAR (80),
				velo VARCHAR (80),
				voie VARCHAR (80)
 				);

SELECT AddGeometryColumn('planet_osm_line', 'the_geom', 3857, 'LINESTRING', 'XY');

INSERT INTO planet_osm_line (
				the_geom,
				acces,
				artificiel,
				bati,
				energie,
				equipement,
				gue,
				loisir,
				nature,
				nom,
				obstacle,
				osm_id,
				pont,
				revetement,
				sensunique,
				tourisme,
				velo,
				voie
)
SELECT
		  		Geometry,
				access,
				man_made,
				building,
				power,
				amenity,
				ford,
				leisure,
				natural,
				name,
				barrier,
				osm_id,
				bridge,
				surface,
				oneway,
				tourism,
				bicycle,
				highway

FROM old_planet_osm_line ;


CREATE TABLE planet_osm_polygon (
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				acces VARCHAR (80),
				artificiel VARCHAR (80),
				bati VARCHAR (80),
				zonage VARCHAR (80),
				bureau VARCHAR (80),
				commerce VARCHAR (80),
				energie VARCHAR (80),
				equipement VARCHAR (80),
				histoire VARCHAR (80),
				hydrograph VARCHAR (80),
				loisir VARCHAR (80),
				marais VARCHAR (80),
				nature VARCHAR (80),
				nom VARCHAR (80),
				obstacle VARCHAR (80),
				osm_id VARCHAR (80),
				piste VARCHAR (80),
				pont VARCHAR (80),
				religion VARCHAR (80),
				revetement VARCHAR (80),
				sport VARCHAR (80),
				tourisme VARCHAR (80),
				voie VARCHAR (80)
				);

SELECT AddGeometryColumn('planet_osm_polygon', 'the_geom', 3857, 'MULTIPOLYGON', 'XY');

INSERT INTO planet_osm_polygon (
				the_geom,
				acces,
				artificiel,
				bati,
				zonage,
				bureau,
				commerce,
				energie,
				equipement,
				histoire,
				hydrograph,
				loisir,
				marais,
				nature,
				nom,
				obstacle,
				osm_id,
				piste,
				pont,
				religion,
				revetement,
				sport,
				tourisme,
				voie
				)

SELECT
				Geometry,
				access,
				man_made,
				building,
				landuse,
				office,
				shop,
				power,
				amenity,
				historic,
				waterway,
				leisure,
				wetland,
				natural,
				name,
				barrier,
				osm_id,
				aeroway,
				bridge,
				religion,
				surface,
				sport,
				tourism,
				highway

FROM old_planet_osm_polygon ;


DROP TABLE old_planet_osm_point ;
DROP TABLE old_planet_osm_line ;
DROP TABLE old_planet_osm_polygon ;

--fin