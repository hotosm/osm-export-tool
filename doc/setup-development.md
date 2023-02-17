## Project Structure

This is a guide to the source code - useful if you'd like to contribute to the Export Tool, deploy the project on your own server, or re-use parts of the project.

`api/` is a Django web application that manages creating, viewing and searching exports, storing feature selections, scheduling jobs, and user accounts via openstreetmap.org OAuth.

`ui/` is a React + ES6 frontend that communicates with the Django API. It handles localization of the user interface, the OpenLayers-based map UI, and the Tag Tree feature selection wizard. (For historical reasons, it also includes some Django views to facilitate logging in with OSM credentials.)

## Development Prerequisites

- Python 3.6 or later, `virtualenv`, `pip`
- PostgreSQL 10+ and PostGIS
  - Recommend [Postgres.app](https://postgresapp.com) which includes PostGIS.
- GDAL/OGR
  - Recommend at least version 2.4 - newer versions available in `ubuntugis` PPAs or Homebrew on Mac
- RabbitMQ, a message queue
- Node.js and [Yarn](https://yarnpkg.com/)

## Overpass API

The Export Tool queries an instance of the Overpass API for source data. Overpass:

- can efficiently perform spatial queries over large quantities of OSM data, including members of ways and relations.
- has built in facilities to ingest minutely diffs from OpenStreetMap.org.
- can create lossless PBF-format exports, which are necessary for some file formats such as OSMand and Garmin .IMG mobile device maps.

Instructions on installing Overpass are available at https://github.com/drolbr/Overpass-API . Alternatively, Overpass can be run via Docker - see `ops/docker-overpass-api`.

- The export tool is configured with an Overpass URL via the environment variable `OVERPASS_API_URL`. This can be a public Overpass instance, a remote instance you manage yourself, or a local instance on your own computer. Public instances may have strict rate limits, so please use them lightly.
- To set up a local Overpass instance, start with a .pbf file. This can be the full planet .pbf from http://planet.openstreetmap.org or a region, e.g. pbfs available from http://download.geofabrik.de/ .
- Optionally, configure Overpass to update itself minutely.

## Development Step-By-Step Guide

### Clone the HOT Export Tool project from GitHub

```bash
git clone https://github.com/hotosm/osm-export-tool.git
cd osm-export-tool

```

### Install Python dependencies

```bash
virtualenv venv  # creates a new environment in venv/
source venv/bin/activate  # activate the virtualenv
pip install -r requirements-dev.txt
```

### Database, database schema, and message queue

- PostgreSQL should be running and listening on the default port, 5432, with the shell user having administrative permissions.
- RabbitMQ should be running and listening on the default port, 5672.

Create and populate a PostgreSQL database named `exports`:

```
createdb exports
psql exports -c "create extension postgis;"
psql exports -c "create extension hstore;"
python manage.py migrate
```

### Compile the front-end application

```bash
cd ui/
yarn install
yarn run dist # for production
yarn start  # will watch for changes and re-compile as necessary
```

### Set required environment variables and start the server

```bash
DEBUG=True python manage.py runserver

# in a different shell
DEBUG=True DJANGO_SETTINGS_MODULE=core.settings.project dramatiq tasks.task_runners -p 1
```

[`direnv`](https://direnv.net/) is a useful tool for managing environment variables using a `.env` file.

​ You should now be able to navigate to http://localhost:8000 and log in via OSM. With `DJANGO_ENV` set to `development`, emails will not be sent, but the email body will appear in your console from `runserver`. Navigate to this link to verify your account. Creating an export will use the public Overpass API. Successful job creations will write the exports to the filesystem to the `export_downloads` directory, a sibling of the `osm-export-tool2` checkout - since the NGINX file server is not running in development, download links won't be valid.

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

- `EXPORT_STAGING_ROOT` path to a directory for staging export jobs
- `EXPORT_DOWNLOAD_ROOT`'path to a directory for storing export downloads
- `EXPORT_MEDIA_ROOT` map this url in your webserver to `EXPORT_DOWNLOAD_ROOT` to serve the exported files
- `OSMAND_MAP_CREATOR_DIR` path to directory where OsmAndMapCreator is installed
- `GARMIN_CONFIG`, `GARMIN_MKGMAP` absolute paths to garmin JARs
- `OVERPASS_API_URL` url of Overpass api endpoint

- `RAW_DATA_API_URL` url of Galaxy api endpoint

- `DATABASE_URL` Database URL. Defaults to `postgres:///exports`
- `DEBUG` Whether to enable debug mode. Defaults to `False` (production).
- `DJANGO_ENV` Django environment. Set to `development` to enable development tools and email logging to console.
- `EMAIL_HOST_USER` SMTP username.
- `EMAIL_HOST_PASSWORD` SMTP password.
- `EMAIL_USE_TLS` Whether to use TLS when sending mail. Optional.
- `HOSTNAME` Publicly-addressable hostname. Defaults to `export.hotosm.org`
- `USE_X_FORWARDED_HOST` - Whether Django is running behind a proxy. Defaults to `False`

## Using the Transifex service

(This section is TBD, as we're currently figuring out workflows for [FormatJS](https://formatjs.io/) JSON strings used by `react-intl`.)

To work with Transifex, you need to create `~/.transifexrc`, and modify its access privileges:

```
chmod 600 ~/.transifexrc
```

Example `.transifexrc` file:

```ini
[https://www.transifex.com]
hostname = https://www.transifex.com
password = my_super_password
token =
username = my_transifex_username
```

### Managing source files

To update source language (English) for Django templates run:

```bash
python manage.py makemessages -l en
```

To update source language for JavaScript files run:

```bash
python manage.py makemessages -d djangojs -l en
```

then, push the new source files to the Transifex service, it will overwrite the current source files

```bash
tx push -s
```

### Pulling latest changes from Transifex

When adding a new language, it's resource file does not exist in the project,
but it's ok as it will be automatically created when pulling new translations from the service. To add a local mapping:

```bash
tx set -r osm-export-tool2.master -l hr locales/hr/LC_MESSAGES/django.po
```

or for JavaScript files:

```bash
tx set -r osm-export-tool2.djangojs -l hr locales/hr/LC_MESSAGES/djangojs.po
```

Once there are some translation updates, pull the latest changes for mapped resources.

For a specific language(s):

```bash
tx pull -l fr,hr
```

For all languages:

```bash
tx pull
```

Finally, compile language files:

```
python manage.py compilemessages
```

### UI Translations

To fetch updated translations for the JavaScript front-end, run:

```bash
cd ui/
yarn run tx:pull
```

To push updated strings to Transifex, run:

```bash
cd ui/

# build the app (to extract new strings)
yarn run pack

yarn run tx:push
```

If / when UI translations pass the 5% complete threshold (defined in `ui/.tx/config` as `minimum_perc`), new JSON files will appear in `ui/app/i18n/locales`. To enable these translations for use, add `react-intl` locale data to `ui/app/app.js` (for date / number formatting) and add options to `ui/app/components/LocaleSelector.js`.
