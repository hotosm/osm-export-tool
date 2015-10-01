"""
    Harness for running sql commands against a spatialite db from python.
    This is work in progress towards a schema translation task.

    From the project directory run:
    ./manage.py runscript spatialite_test --settings=hot_exports.settings -v2
    Depends on django-extensions.
"""

import os
import sqlite3
from string import Template


def run(*script_args):
    path = os.path.dirname(os.path.realpath(__file__))
    translations = open(path + '/translations.txt')
    trans = []
    for line in translations.readlines():
        if line.strip() == '':
            continue
        pair = line.strip().split(',')
        trans.append(pair)
    for entry in trans:
        print entry[0], entry[1]

    print trans
    conn = sqlite3.connect('/home/ubuntu/export_downloads/0c937545-cb43-4f9a-97b4-6e90e0c791a7/query.sqlite')

    # load spatialite extension
    conn.enable_load_extension(True)
    cmd = "SELECT load_extension('libspatialite')"
    cur = conn.cursor()
    cur.execute(cmd)

    # drop the planet_osm_point table and related indexes
    cur.execute("SELECT DiscardGeometryColumn('planet_osm_point', 'GEOMETRY')")
    cur.execute("DROP TABLE idx_planet_osm_point_GEOMETRY")
    cur.execute('DROP TABLE planet_osm_point')

    # get column info
    cur.execute('PRAGMA table_info(planet_osm_point_temp)')
    point_columns = cur.fetchall()
    new_columns = []
    for column in point_columns:
        column_name = column[1]
        column_type = column[2]
        # translate column

        new_columns.append('{0} {1}'.format(column_name, column_type))

    # create the new table
    sql_templ = Template("""
            CREATE TABLE planet_osm_point(
                $columns
            );
    """)

    colstr = ','.join(new_columns)
    sql = sql_templ.safe_substitute({'columns': colstr})
    # cursor = conn.execute('ALTER TABLE planet_osm_point RENAME TO planet_osm_point_temp;')
    cur.execute(sql)

    # add the geometry column and spatial index
    cur.execute("SELECT RecoverGeometryColumn('planet_osm_point', 'GEOMETRY', 4326, 'POINT', 'XY')")
    cur.execute("SELECT CreateSpatialIndex('planet_osm_point', 'GEOMETRY')")

    # copy data from planet_osm_point_temp to planet_osm_point
    cur.execute('INSERT INTO planet_osm_point SELECT * FROM planet_osm_point_temp;')
    conn.commit()
    cur.close()
