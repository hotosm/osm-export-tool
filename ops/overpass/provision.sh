export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y
apt-get install -y nginx fcgiwrap python3-pip
pip3 install boto3

adduser --disabled-password --gecos "" overpass

wget https://hotosm-export-tool.s3.amazonaws.com/osm-3s-v0.7.55.tgz
tar -xzf osm-3s-v0.7.55.tgz
rm osm-3s-v0.7.55.tgz
mv osm-3s_v0.7.55/ /home/overpass/
chown -R overpass:overpass /home/overpass/osm-3s_v0.7.55/
chown overpass:overpass /home/overpass/cloudwatch_metrics.py
chmod +x /home/overpass/cloudwatch_metrics.py
mv /tmp/motd /etc/motd
mv /tmp/cloudwatch_metrics.py /home/overpass/cloudwatch_metrics.py
mv /tmp/nginx.conf /etc/nginx.conf
mv /tmp/fcgiwrap.service /etc/systemd/system/fcgiwrap.service
chmod 775 /home/overpass/osm-3s_v0.7.55/cgi-bin/interpreter
chmod 775 /home/overpass/osm-3s_v0.7.55/cgi-bin/timestamp
chmod 775 /home/overpass/osm-3s_v0.7.55/cgi-bin/augmented_diff
chmod 775 /home/overpass/osm-3s_v0.7.55/cgi-bin/augmented_diff_status
