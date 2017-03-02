set -e

sudo apt-get update

# add UbuntuGIS ppa.
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update

sudo apt-get install -y libspatialite5 libgdal1h libgeos-c1v5 liblwgeom-2.1.2
sudo apt-get install -y postgresql-9.3-postgis-2.1

# Install core dependencies.
sudo apt-get install -y libpq-dev python-dev python-pip git
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y gdal-bin libgdal-dev python-gdal

# dependency for python LXML library.
sudo apt-get install -y libxslt1-dev

# Message queue used for Celery. For more detailed installation see http://www.rabbitmq.com/install-debian.html
sudo apt-get install -y rabbitmq-server

# dependencies for 3rd party tools in the Export pipeline.
sudo apt-get install -y osmctools spatialite-bin libspatialite-dev default-jre zip unzip
