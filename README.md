OSM Export Tool
======

<!---![alt text](https://travis-ci.org/hotosm/osm-export-tool2.svg?branch=master)--->

**Osm Export Tool** platform allows you to create custom OpenStreetMap exports for various HOT regions. You can specify an area of interest and a list of features (OpenStreetMap tags) for the export. A current OpenStreetMap data extract for that area in various data formats is then created for you within minutes.

The live site http://export.hotosm.org is currently still powered by the older version 1 code living at https://github.com/hotosm/hot-exports

This repo contains the newly re-written version 2 of the OSM exports tool.

## Installation Instructions
Some prior experience with Django would be helpful, but not strictly necessary.
### Update Packages
<pre>
$ sudo apt-get update
$ sudo apt-get upgrade
</pre>

### Python
HOT Exports requires Python 2.7.x. 

### pip
To install pip, run:

<code>$ sudo apt-get install python-pip</code>

### Git
Git is used for version control. To check your version, and if you have it installed:

<code>$ git --version</code> or run <code>$ sudo apt-get install git</code>

### Virtualenv
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

### Postgres
Install PostgreSQL / PostGIS and its dependencies,

<code>$ sudo apt-get install libpq-dev python-dev</code>

<code>$ sudo apt-get install postgresql postgresql-contrib</code>

<code>$ sudo apt-get install postgis postgresql-9.3-postgis-2.1</code>

### Create the database and role
<pre>
$ sudo su - postgres
$ createdb 'hot_exports_dev'
$ create role hot with password '<-password->'
</pre>

You might need to update the <code>pg_hba.conf</code> file to allow localhost connections via tcp/ip or
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

### Install GDAL

We need gdal >=1.10.0

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
</pre>

### Install third-party dependencies
The HOT Export pipeline depends on a number of third-party tools.

<code>$ sudo apt-get install osmctools</code>

<code>$ sudo apt-get install libspatialite5 libspatialite-dev</code>

#### Garmin

Download the latest version of the __mkgmap__ utility for making garmin IMG files from [http://www.mkgmap.org.uk/download/mkgmap.html](http://www.mkgmap.org.uk/download/mkgmap.html)

Download the latest version of the __splitter__ utility for splitting larger osm files into tiles. [http://www.mkgmap.org.uk/download/splitter.html](http://www.mkgmap.org.uk/download/splitter.html)

Create a directory and unpack the <code>mkgmap</code> and <code>splitter</code> archives into it.

#### OSMAnd OBF

For details on the OSMAnd Map Creator utility see [http://wiki.openstreetmap.org/wiki/OsmAndMapCreator](http://wiki.openstreetmap.org/wiki/OsmAndMapCreator)

Download the OSMAnd MapCreator from [http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip](http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip).
Unpack this into a directory somewhere.

### Install RabbitMQ

HOT Exports depends on the **rabbitmq-server**. For more detailed installation instructions see [http://www.rabbitmq.com/install-debian.html](http://www.rabbitmq.com/install-debian.html).
The default configuration should be fine for development purposes.

<code>$ sudo apt-get install rabbitmq-server</code>

### Checkout the HOT Export Tool source

In the hotosm project directory run:

<code>$ git clone git@github.com:hotosm/osm-export-tool2.git</code>

### Install lxml dependencies

<code>sudo apt-get install libxml2-dev libxslt-dev python-dev</code>

### Install the project's python dependencies

From the project directory, install the dependencies into your virtualenv:

<code>$ pip install -r requirements-dev.txt</code>

or

<code>$ pip install -r requirements.txt</code>

### Project Configuration

Create a <code>settings_private.py</code> file in the hot_exports directory and add the following:

<pre>
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'hot_exports_dev',
        'OPTIONS': {
            'options': '-c search_path=exports,public'
        },
        'CONN_MAX_AGE': None,
        'HOST': 'localhost',
        'USER': 'hot',
        'PASSWORD': 'your password',
    }
}
</pre>

Update the <code>settings.py</code> file. Set the following config variables:

Set <code>OSMAND_MAP_CREATOR_DIR</code> to the directory where you installed the OSMAnd MapCreator.

Set <code>GARMIN_CONFIG</code> to point to the **absolute** path to the garmin configuration file, ./utils/conf/garmin_config.xml by default.

Update the <code>utils/conf/garmin_config.xml</code> file. Update the <code>garmin</code> and <code>splitter</code> elements to point to the
absolute location of the <code>mkgmap.jar</code> and <code>splitter.jar</code> utilites.

Once you've got all the dependencies installed, run <code>./manage.py migrate</code> to set up the database tables etc..
Then run <code>./manage.py runserver</code> to run the server.
You should then be able to browse to [http://localhost:8000/](http://localhost:8000/)

## Celery Workers

HOT Exports depends on the [Celery](http://celery.readthedocs.org/en/latest/index.html) distributed task queue. As export jobs are created
they are pushed to a Celery Worker for processing. At least two celery workers need to be started as follows:

From a 'hotosm' virtualenv directory (use screen), run:

<code>$ celery -A hot_exports worker --loglevel debug --logfile=celery.log</code>.

This will start a celery worker which will process export tasks. An additional celery worker needs to be started to handle purging of expired unpublished
export jobs. From another hotosm virtualenv terminal session, run:

<code>$ celery -A hot_exports beat --loglevel debug --logfile=celery-beat.log</code>

See the <code>CELERYBEAT_SCHEDULE</code> setting in <code>settings.py</code>.

For more detailed information on Celery Workers see [here](http://celery.readthedocs.org/en/latest/userguide/workers.html)


## Front end tools

HOT Exports uses bower to manage javascript dependencies.

<pre>
sudo apt-get install nodejs
sudo apt-get install npm
sudo npm -g install bower
sudo npm -g install yuglify
</pre>

## Using Transifex service

To work with Transifex you need to create `~/.transifexrc`, and modify it's access privileges `chmod 600 ~/.transifexrc`

Example `.transifexrc` file:

    [https://www.transifex.com]
    hostname = https://www.transifex.com
    password = my_super_password
    token =
    username = my_transifex_username

### Manage source files

* update source language (English) file
  * `python manage.py makemessages -l en`

* push the new source file to Transifex service, it will overwrite current source file
  * `tx push -s`

### Pulling latest changes from the Transfex

* when adding a new language, it's resource file does not exists in the project, but it's ok as it will be automatically created when pulling new translations from the service
  * add a local mapping: `tx set -r osm-export-tool2.master -l hr osmtm/locale/hr/LC_MESSAGES/osmtm.po`
* after there are some translation updates, pull latest changes for mapped resources
  * for a specific language(s):
    * `tx pull -l fr,hr`
  * for all languages:
    * `tx pull`
* finally, compile language files
  * `python manage.py compilemessages`
