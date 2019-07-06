apt update
apt upgrade -y
apt install -y nginx fcgiwrap

wget https://hotosm-export-tool.s3.amazonaws.com/osm-3s-v0.7.55.tgz
tar -xzf osm-3s-v0.7.55.tgz
rm osm-3s-v0.7.55.tgz
