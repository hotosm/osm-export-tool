#http://wiki.openstreetmap.org/wiki/Overpass_API/Installation

set -e
apt-get update
apt-get install -y --force-yes --no-install-recommends g++ make expat libexpat1-dev zlib1g-dev curl fcgiwrap nginx wget
curl -sfo osm-3s_v0.7.54.tar.gz http://dev.overpass-api.de/releases/osm-3s_v0.7.54.tar.gz
tar -zxvf osm-3s_v0.7.54.tar.gz
cd osm-3s_v0.7.54
./configure CXXFLAGS="-O2" --prefix="/srv/osm3s"
make -j $(nproc) install

# attach a 400gb volume to /mnt, and edit fstab to mount it on boot
# clone down an "attic" db from link above to /mnt
