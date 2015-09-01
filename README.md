OSM Export Tool
======
**Osm Export Tool** platform allows you to create custom OpenStreetMap exports for various HOT regions. You can specify an area of interest and a list of features (OpenStreetMap tags) for the export. A current OpenStreetMap data extract for that area in various data formats is then created for you within minutes.

## Installation Instructions
Some prior experience with Django would be incredibly helpful, but not strictly necessary.
#####-Update Packages
$ sudo apt-get update
$ sudo apt-get upgrade
#####-Python
Unix environments come pre-installed with Python. To check version, run the command:
$ python -V
$ python3 -V
If you have 2.7.x version, you can go ahead.
#####-easy_install and pip
easy_install and pip are Python Package Managers, making it much easier to install and upgrade Python packages (and package dependencies).
To download easy_install, go to the Python Package Index (PyPI).
You need to download setuptools, which includes easy_install.
Download the package egg (.egg), then install it directly from the file.
To install pip, run:
$ easy_install pip
#####-Git
Git will be used for version control. To check your version, if you have installed:
$ git --version
#####-Virtualenv
virtualenv (virtual environment) creates self-contained development environments to prevent different versions of libraries/packages from messing with each other.
$ pip install virtualenv
Clone/fork the project on github in any desired directory.
$ cd osm-export-tool2
$ virtualenv env
$ source env/bin/activate
You should see (env) before your prompt, (env)$, indicating that you’re running within the ‘env’ virtualenv.
To exit the virtualenv, type the following command:
$ deactivate

#####-django
In the virtualenv,
$ pip install django
#####-Postgres
Install PostgreSQL and its dependencies,
$ sudo apt-get install libpq-dev python-dev
$ sudo apt-get install postgresql postgresql-contrib
#####-Create the database and role
$ sudo su - postgres
$ createdb 'hot_exports_dev'
$ create role hot with password '<-password->'
set the user to be 'hot' and password to be above password in settings_private.py
Type psql
$ ALTER ROLE hot SUPERUSER;
$ ALTER ROLE hot WITH LOGIN;
$ GRANT ALL PRIVILEGES ON DATABASE hot_exports_dev TO hot;
$ CREATE EXTENSION POSTGIS;
$ CREATE EXTENSION HSTORE;

#####-Install GDAL
For ubuntu, following packages are required before installing GDAL
$ sudo apt-get install python-software-properties
$ sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
$ sudo apt-get update
To install the python GDAL bindings into your virtualenv you need to tell pip where to find the libgdal header files, so in your shell run:
$ export CPLUS_INCLUDE_PATH=/usr/include/gdal
$ export C_INCLUDE_PATH=/usr/include/gdal
$ pip install GDAL=1.11.2

#####-Final Step:
Install the dependencies into your virtualenv:
$ pip install -r /path/to/requirements-dev.txt
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
