apt update
apt upgrade -y
add-apt-repository -y ppa:ubuntugis/ppa
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
add-apt-repository -y "deb https://dl.yarnpkg.com/debian/ stable main"
apt install -y \
build-essential \
curl \
default-jre-headless \
gdal-bin \
git \
language-pack-en-base \
libffi-dev \
libgdal-dev \
libmagic1 \
libpq-dev \
libqt5core5a \
libsqlite3-mod-spatialite \
libspatialite7 \
libspatialite-dev \
libproxy1v5 \
libxslt1-dev \
nodejs \
osmctools \
postgresql-client \
python-dev \
python-pip \
python-setuptools \
python-wheel \
python-gdal \
spatialite-bin \
unzip \
yarn \
zip
apt clean
