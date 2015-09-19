OSM Export Tool
======
**Osm Export Tool** platform allows you to create custom OpenStreetMap exports for various HOT regions. You can specify an area of interest and a list of features (OpenStreetMap tags) for the export. A current OpenStreetMap data extract for that area in various data formats is then created for you within minutes.

The live site http://export.hotosm.org is currently still powered by the older version 1 code living at https://github.com/hotosm/hot-exports

This repo contains the newly re-written version 2 of the OSM exports tool.

## Installation Instructions
Some prior experience with Django would be helpful, but not strictly necessary.
##### Update Packages
<pre>
$ sudo apt-get update
$ sudo apt-get upgrade
</pre>

##### Python
Unix environments come pre-installed with Python. To check version, run the command:

<code>$ python -V</code>

<code>$ python3 -V</code>

HOT Exports requires Python 2.7.x. If you have 2.7.x installed, you can go ahead.

##### pip
To install pip, run:

<code>$ sudo apt-get install python-pip</code>

##### Git
Git is used for version control. To check your version, and if you have it installed:

<code>$ git --version</code> or run <code>$ sudo apt-get install git</code>

##### Virtualenv
Virtualenv (virtual environment) creates self-contained environments to prevent different versions of python libraries/packages from conflicting with each other.

To make your life easier install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)

<code>$sudo pip install virtualenvwrapper</code>

Add the following to <code>.bashrc</code> or <code>.profile</code>

<pre>
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/dev 
source /usr/local/bin/virtualenvwrapper.sh
</pre>

Run <code>source ~/.bashrc</code>

Run <code>mkvirtualenv hotosm</code> to create the hotosm virtual environment.

Change to the <code>$HOME/dev/hotosm</code> directory and run <code>workon hotosm</code>.

##### Postgres
Install PostgreSQL / PostGIS and its dependencies,

<code>$ sudo apt-get install libpq-dev python-dev</code>

<code>$ sudo apt-get install postgresql postgresql-contrib</code>

<code>$ sudo apt-get install postgis postgresql-9.3-postgis-2.1</code>

##### Create the database and role
<pre>
$ sudo su - postgres
$ createdb 'hot_exports_dev'
$ create role hot with password '<-password->'
</pre>
You might need to update the pg_hba.conf file to allow localhost connections via tcp/ip or
allow trusted connections from localhost.

Run <code>$ psql -h localhost -U hot -W hot_exports_dev</code>
<pre>
$ ALTER ROLE hot SUPERUSER;
$ ALTER ROLE hot WITH LOGIN;
$ GRANT ALL PRIVILEGES ON DATABASE hot_exports_dev TO hot;
$ CREATE EXTENSION POSTGIS;
$ CREATE EXTENSION HSTORE;
</pre>
Create the exports schema
<pre>
$ CREATE SCHEMA exports AUTHORIZATION hot;
</pre>
##### Install GDAL
For ubuntu, following packages are required before installing GDAL
<pre>
$ sudo apt-get install python-software-properties
$ sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
$ sudo apt-get update
$ sudo apt-get install gdal-bin libgdal-dev
</pre>
To install the python GDAL bindings into your virtualenv you need to tell pip where to find the libgdal header files, so in your shell run:
<pre>
$ export CPLUS_INCLUDE_PATH=/usr/include/gdal
$ export C_INCLUDE_PATH=/usr/include/gdal
$ pip install GDAL=1.11.2
</pre>
##### Install third-party dependencies
The HOT Export pipeline depends on a number of third-party tools.

<code>$ sudo apt-get install osmctools</code>

<code>$ sudo apt-get install libspatialite5</code>

###### Garmin

Download the latest version of the __mkgmap__ utility for making garming img files from [http://www.mkgmap.org.uk/download/mkgmap.html](http://www.mkgmap.org.uk/download/mkgmap.html)

Download the latest version of the __splitter__ utility for splitting larger osm files into tiles. [http://www.mkgmap.org.uk/download/splitter.html](http://www.mkgmap.org.uk/download/splitter.html)


##### Final Step:
Install the dependencies into your virtualenv:
<pre>
$ pip install -r /path/to/requirements-dev.txt
</pre>
Once you've got all the dependencies installed, run ./manage.py migrate to set up the database tables etc..
Then run ./manage.py runserver to run the server.
You should then be able to browse to http://localhost:8000/

---------------------------------------------------------------------------------------

# Transifex workflow


## Using Transifex service

* to work with Transifex you need to create `~/.transifexrc`, and modify it's access privileges `chmod 600 ~/.transifexrc`

Example `.transifexrc` file:

    [https://www.transifex.com]
    hostname = https://www.transifex.com
    password = my_super_password
    token =
    username = my_transifex_username

## Manage source files

* update source language (English) file
  * `python manage.py makemessages -l en`

* push the new source file to Transifex service, it will overwrite current source file
  * `tx push -s`

## Pulling latest changes from the Transfex

* when adding a new language, it's resource file does not exists in the project, but it's ok as it will be automatically created when pulling new translations from the service
  * add a local mapping: `tx set -r osm-export-tool2.master -l hr osmtm/locale/hr/LC_MESSAGES/osmtm.po`
* after there are some translation updates, pull latest changes for mapped resources
  * for a specific language(s):
    * `tx pull -l fr,hr`
  * for all languages:
    * `tx pull`
* finally, compile language files
  * `python manage.py compilemessages`
