[![Stories in Ready](https://badge.waffle.io/hotosm/osm-export-tool2.png?label=ready&title=Ready)](https://waffle.io/hotosm/osm-export-tool2)
OSM Export Tool
======

<!---![alt text](https://travis-ci.org/hotosm/osm-export-tool2.svg?branch=master)--->

**Osm Export Tool** platform allows you to create custom OpenStreetMap exports for various HOT regions. You can specify an area of interest and a list of features (OpenStreetMap tags) for the export. A current OpenStreetMap data extract for that area in various data formats is then created for you within minutes.

This repo contains the newly re-written version 2 of the OSM exports tool. The live site http://export.hotosm.org is now powered by this repo. The older version 1 site is still available at: http://old-export.hotosm.org/ running code from this repo: https://github.com/hotosm/hot-exports

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

Run <code>mkvirtualenv --system-site-packages hotosm</code> to create the hotosm virtual environment.

Change to the <code>$HOME/dev/hotosm</code> directory and run <code>workon hotosm</code>.

### Postgres
Install PostgreSQL / PostGIS and its dependencies,

<code>$ sudo apt-get install libpq-dev python-dev</code>

<code>$ sudo apt-get install postgresql postgresql-contrib</code>

<code>$ sudo apt-get install postgis postgresql-9.3-postgis-2.1</code>

### Create the database and role
<pre>
$ sudo -u postgres createuser -s -P hot
$ sudo -u postgres createdb -O hot hot_exports_dev
</pre>

You might need to update the <code>pg_hba.conf</code> file to allow localhost connections via tcp/ip or
allow trusted connections from localhost.

Create the exports schema

<pre>
$ psql -U hot -h localhost -d hot_exports_dev -c "CREATE SCHEMA exports AUTHORIZATION hot"
</pre>

### Install GDAL

<pre>
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
$ sudo apt-get update
$ sudo apt-get install gdal-bin libgdal-dev python-gdal
</pre>

### Install third-party dependencies
The HOT Export pipeline depends on a number of third-party tools.

<code>$ sudo apt-get install osmctools</code>

<code>$ sudo apt-get install spatialite-bin libspatialite5 libspatialite-dev</code>

<code>$ sudo apt-get install default-jre zip unzip</code>

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

### Install the project's python dependencies

Install <code>libxslt1-dev</code> (it's an <code>lxml</code> dependency):

```bash
sudo apt-get install libxslt1-dev
```

From the project directory, install the dependencies into your virtualenv:

<code>$ pip install -r requirements-dev.txt</code>

or

<code>$ pip install -r requirements.txt</code>


### Project Settings

Create a copy of <code>core/settings/dev_dodobas.py</code> and update to reflect your development environment. <code>core/settings/dev.py</code> exists for this purpose.

Look at <code>core/settings/project.py</code> and make sure you update or override the following configuration variables in your development settings:

**EXPORT_STAGING_ROOT** = 'path to a directory for staging export jobs'

**EXPORT_DOWNLOAD_ROOT** = 'path to a directory for storing export downloads'

**EXPORT_MEDIA_ROOT** = '/downloads/' (map this url in your webserver to EXPORT_DOWNLOAD_ROOT to serve the exported files)

**OSMAND_MAP_CREATOR_DIR** = 'path to directory where OsmAndMapCreator is installed'

**GARMIN_CONFIG** = 'absolute path to utils/conf/garmin_config.xml'

**OVERPASS_API_URL** = 'url of your local overpass api endpoint (see Overpass API below)'

Edit <code>core/settings/dev.py</code> to ensure that the database connection information is correct.

Update the <code>utils/conf/garmin_config.xml</code> file. Update the <code>garmin</code> and <code>splitter</code> elements to point to the
absolute location of the <code>mkgmap.jar</code> and <code>splitter.jar</code> utilites.

Set the active configuration (<code>you_settings_module</code> can be <code>dev</code> or the basename of your copy of <code>core/settings/dev_dodobas.py</code>):

<code>export DJANGO_SETTINGS_MODULE=core.settings.your_settings_module</code> (defaults to `core.settings.dev` in `manage.py`)

Once you've got all the dependencies installed, run <code>./manage.py migrate</code> to set up the database tables etc..
Then run <code>./manage.py runserver</code> to run the server.
You should then be able to browse to [http://localhost:8000/](http://localhost:8000/)

If you're running this in a virtual machine, use <code>./manage.py runserver 0.0.0.0:8000</code> to have Django listen on all interfaces and make it possible to connect from the VM host.

## Overpass API

The HOT Exports service uses a local instance of [Overpass v07.52](http://overpass-api.de/) for data extraction.
Detailed instructions for installing Overpass are available [here](http://wiki.openstreetmap.org/w/index.php?title=Overpass_API/Installation&redirect=no).

Download a (latest) planet pbf file from (for example) [http://ftp.heanet.ie/mirrors/openstreetmap.org/pbf/](http://ftp.heanet.ie/mirrors/openstreetmap.org/pbf/).

If you're doing development you don't need the whole planet so download a continent or country level extract from [http://download.geofabrik.de/](http://download.geofabrik.de/),
and update the `osmconvert` command below to reflect the filename you've downloaded.

To prime the database we've used `osmconvert` as follows:

<code>osmconvert --out-osm planet-latest.osm.pbf | ./update_database --meta --db-dir=$DBDIR --flush-size=1</code>

If the dispatcher fails to start, check for, and remove <code>osm3s_v0.7.52_osm_base</code> from <code>/dev/shm</code>.

We apply minutely updates as per Overpass installation instructions, however this is not strictly necessary for development purposes.

## Celery Workers

HOT Exports depends on the [Celery](http://celery.readthedocs.org/en/latest/index.html) distributed task queue. As export jobs are created
they are pushed to a Celery Worker for processing. At least two celery workers need to be started as follows:

From a 'hotosm' virtualenv directory (use screen), run:

<code>export DJANGO_SETTINGS_MODULE=core.settings.your_settings_module</code>

<code>$ celery -A core worker --loglevel debug --logfile=celery.log</code>.

This will start a celery worker which will process export tasks. An additional celery worker needs to be started to handle purging of expired unpublished
export jobs. From another hotosm virtualenv terminal session in the project top-level directory, run:

<code>export DJANGO_SETTINGS_MODULE=core.settings.your_settings_module</code>

<code>$ celery -A core beat --loglevel debug --logfile=celery-beat.log</code>

See the <code>CELERYBEAT_SCHEDULE</code> setting in <code>core/settings/celery.py</code>.

For more detailed information on Celery Workers see [here](http://celery.readthedocs.org/en/latest/userguide/workers.html)

For help with daemonizing Celery workers see [here](http://celery.readthedocs.org/en/latest/tutorials/daemonizing.html)

## Using Transifex service

To work with Transifex you need to create `~/.transifexrc`, and modify it's access privileges

`chmod 600 ~/.transifexrc`

Example `.transifexrc` file:

    [https://www.transifex.com]
    hostname = https://www.transifex.com
    password = my_super_password
    token =
    username = my_transifex_username

### Managing source files

To update source language (English) for Django templates run:

`python manage.py makemessages -l en`

To update source language for javascript files run:

`python manage.py makemessages -d djangojs -l en`


then, push the new source files to the Transifex service, it will overwrite the current source files

`tx push -s`

### Pulling latest changes from Transifex

When adding a new language, it's resource file does not exist in the project,
but it's ok as it will be automatically created when pulling new translations from the service. To add a local mapping:

`tx set -r osm-export-tool2.master -l hr locales/hr/LC_MESSAGES/django.po`

or for javascript files:

`tx set -r osm-export-tool2.djangojs -l hr locales/hr/LC_MESSAGES/djangojs.po`


Once there are some translation updates, pull the latest changes for mapped resources

For a specific language(s):

`tx pull -l fr,hr`

For all languages:

`tx pull`

Finally, compile language files

`python manage.py compilemessages`
