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
postgis \
python-dev \
python-pip \
python-setuptools \
python-wheel \
python-gdal \
spatialite-bin \
unzip \
yarn \
zip \
nginx \
qt5-default
apt clean

wget https://hotosm-export-tool.s3.amazonaws.com/mkgmap-r3890.zip
unzip mkgmap-r3890.zip -d /usr/local
mv /usr/local/mkgmap-r3890 /usr/local/mkgmap
rm mkgmap-r3980.zip

wget https://hotosm-export-tool.s3.amazonaws.com/splitter-r583.zip
unzip splitter-r583.zip -d /usr/local
mv /usr/local/splitter-r583 /usr/local/splitter
rm splitter-r583.zip

wget https://hotosm-export-tool.s3.amazonaws.com/OsmAndMapCreator-main.zip
mkdir /usr/local/OsmAndMapCreator
unzip OsmAndMapCreator-main.zip -d /usr/local/OsmAndMapCreator
rm OsmAndMapCreator-main.zip

wget https://hotosm-export-tool.s3.amazonaws.com/omim-build-release-9ac133b.tgz
sudo tar -xzf omim-build-release-9ac133b.tgz -C /usr/local/
sudo mv /usr/local/omim-build-release /usr/local/omim
