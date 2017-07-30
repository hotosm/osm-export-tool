OSM Export Tool
======

[![Join the chat at https://gitter.im/hotosm/osm-export-tool2](https://badges.gitter.im/hotosm/osm-export-tool2.svg)](https://gitter.im/hotosm/osm-export-tool2?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![CircleCI](https://circleci.com/gh/hotosm/osm-export-tool2.svg?style=svg)](https://circleci.com/gh/hotosm/osm-export-tool2)

The **Export Tool** creates OpenStreetMap exports for GIS programs and mobile devices. It outputs files in various tabular formats based on an input area of interest polygon and a selection of OpenStreetMap tags. It is synchronized minutely with the main OSM database, so exports can be created to accompany real-time humanitarian mapping efforts. 

The latest version of the Export Tool is available at http://exports-prod.hotosm.org . All users are recommended to use this version.

The previous (version 2) iteration of the Export Tool is available at http://export.hotosm.org . This version is slower and less featureful than the newest version.

## Project Structure
This is a guide to the source code - useful if you'd like to contribute to the Export Tool, deploy the project on your own server, or re-use parts of the project.

`utils/`  contains Python classes responsible for downloading and transforming OSM data into each file format based on a GEOS geometry and a `FeatureSelection` object. Many of these are wrappers for GDAL/OGR commands. This module can be used independently of the web application for creating exports from the command line.

`feature_selection/` contains a parser for YAML feature selections that define how OSM data is mapped to tabular formats. More documentation on the YAML format is available at http://exports-prod.hotosm.org/v3/help/yaml .

`api/` is a Django web application that manages creating, viewing and searching exports, storing feature selections,  scheduling jobs, and user accounts via openstreetmap.org OAuth.

`ui/` is a React + ES6 frontend that communicates with the Django web application. It handles localization of the user interface, the OpenLayers-based map UI, and the Tag Tree feature selection wizard.

## Development Prerequisites

The Export Tool has several dependencies. As an alternative, use Docker to manage the project's environment, in which case you will need a Docker runtime. 

* Python 2.7, virtualenv, pip
* PostgreSQL 9+ and PostGIS
* GDAL/OGR
* RabbitMQ, a message queue
* node.js and yarn

## Overpass API

The Export tool queries an instance of the Overpass API for source data. Overpass:

* can efficiently perform spatial queries over a large amount of OSM data, including members of ways and relations.
* Has built in facilities to update OSM from minutely diffs.
* Can create lossless PBF-format exports, which are necessary for some file formats such as OSMand and Garmin .IMG mobile device maps.

Instructions on installing Overpass are available at https://github.com/drolbr/Overpass-API . Alternatively, Overpass can be run via Docker - see `ops/docker-overpass-api`.

* The export tool is configured with an Overpass URL via the environment variable `OVERPASS_API_URL`. This can be a public Overpass instance, a remote instance you manage yourself, or a local instance on your own computer. Public instances may have strict rate limits, so please use them lightly.
* To set up a local Overpass instance, start with a .pbf file. This can be the full planet .pbf from http://planet.openstreetmap.org or a region, e.g. pbfs available from http://download.geofabrik.de/ . 
* Optionally, configure Overpass to update itself minutely. 



## Development Step-By-Step Guide

### Checkout the HOT Export Tool source

    git clone git@github.com:hotosm/osm-export-tool2.git
    cd osm-export-tool2

### create and install python environment

    virtualenv myvirtualenv # creates a new environment in myvirtualenv/
    source myvirtualenv/bin/activate
    pip install -r requirements-dev.txt

###  database, database schema and message queue

* PostgreSQL should be running and listening on the default port, 5432, with the shell user having administrative permissions.

* RabbitMQ should be running and listening on the default port, 5672.

    createdb exports
    python manage.py migrate

### compile the frontend application

    cd ui/
    yarn install
    yarn start # will watch for changes and re-compile as necessary

### set required environment variables and start the server

    DJANGO_ENV=development DEBUG=True python manage.py runserver
    # in a different shell
    DJANGO_ENV=development DEBUG=True celery -A core worker

​    You should now be able to navigate to localhost:8000 and log in via OSM. With DJANGO_ENV set to `development`, emails will not be sent, but the email body will appear in your console from `runserver`. Navigate to this link to verify your account. Creating an export will use the public Overpass API. Successful job creations will write the exports to the filesystem to the `export_downloads` directory, a sibling of the `osm-export-tool2` checkout - since the NGINX file server is not running in development, download links won't be valid.
### Other dependencies

See `core/settings/project.py` for environment variables to configure other optional runtime dependencies.

#### Garmin .IMG

Creating .IMG files requires the `mkgmap` and `splitter` tools.

[http://www.mkgmap.org.uk/download/mkgmap.html](http://www.mkgmap.org.uk/download/mkgmap.html)

[http://www.mkgmap.org.uk/download/splitter.html](http://www.mkgmap.org.uk/download/splitter.html)

#### OSMAnd .OBF

For details and download links to the OSMAnd Map Creator utilities, see [http://wiki.openstreetmap.org/wiki/OsmAndMapCreator](http://wiki.openstreetmap.org/wiki/OsmAndMapCreator)

### List of environment variables

Most of these environment variables have reasonable default settings.

* `EXPORT_STAGING_ROOT`  path to a directory for staging export jobs
* `EXPORT_DOWNLOAD_ROOT`'path to a directory for storing export downloads
* `EXPORT_MEDIA_ROOT` map this url in your webserver to `EXPORT_DOWNLOAD_ROOT` to serve the exported files
* `OSMAND_MAP_CREATOR_DIR` path to directory where OsmAndMapCreator is installed
* `GARMIN_CONFIG`, `GARMIN_MKGMAP` absolute paths to garmin JARs
* `OVERPASS_API_URL` url of Overpass api endpoint
* `BROKER_URL`  Celery broker URL. Defaults to `amqp://guest:guest@localhost:5672/`
* `DATABASE_URL`  Database URL. Defaults to `postgres:///exports`
* `DEBUG`  Whether to enable debug mode. Defaults to `False` (production).
* `DJANGO_ENV`  Django environment. Set to `development` to enable development tools and email logging to console.
* `EMAIL_HOST`  SMTP host. Optional.
* `EMAIL_HOST_USER`  SMTP username. Optional.
* `EMAIL_HOST_PASSWORD` SMTP password. Optional.
* `EMAIL_PORT` SMTP port. Optional.
* `EMAIL_USE_TLS`  Whether to use TLS when sending mail. Optional.
* `HOSTNAME` Publicly-addressable hostname. Defaults to `export.hotosm.org`
* `USE_X_FORWARDED_HOST` - Whether Django is running behind a proxy. Defaults to `False`

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

## Environment Variables


