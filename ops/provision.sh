#!/usr/bin/env bash

set -eo pipefail

export DEBIAN_FRONTEND=noninteractive

>&2 echo "Adding PostgreSQL apt repository..."

# not using add-apt-repository in order to avoid conflicts w/ rewrites to
# /etc/apt/sources.list on boot
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/postgresql.list
curl -sf https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt update

>&2 echo "Installing apt packages..."

apt install -y --no-install-recommends \
  postgresql-9.6-postgis-2.3 libpq-dev python-dev python-pip gdal-bin \
  libgdal-dev python-gdal osmctools spatialite-bin libspatialite5 \
  libspatialite-dev default-jre zip unzip rabbitmq-server git libxslt1-dev \
  postfix build-essential postgresql-9.6-postgis-2.3-scripts nginx \
  postgresql-contrib-9.6

>&2 echo "Cloning git repository..."

git clone https://github.com/hotosm/osm-export-tool2.git ${app_root}
cd ${app_root}

>&2 echo "Installing Python packages..."

pip install -r requirements-dev.txt
pip install gunicorn

>&2 echo "Fetching and installing 3rd-party utilities..."

curl -sfL http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip -o /tmp/osmandmapcreator.zip
unzip /tmp/osmandmapcreator.zip -d ${base_dir}/osmandmapcreator
rm /tmp/osmandmapcreator.zip

curl -sfL http://www.mkgmap.org.uk/download/mkgmap-r3672.zip -o /tmp/mkgmap.zip
unzip /tmp/mkgmap.zip -d ${base_dir}/mkgmap
rm /tmp/mkgmap.zip

curl -sfL http://www.mkgmap.org.uk/download/splitter-r435.zip -o /tmp/splitter.zip
unzip /tmp/splitter.zip -d ${base_dir}/splitter
rm /tmp/splitter.zip

mkdir -p ${exports_dir}

>&2 echo "Placing configuration files..."

cat <<EOF > core/settings/site.py
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .prod import *  # NOQA

ALLOWED_HOSTS = ['${fqdn}']
SESSION_COOKIE_DOMAIN = '${fqdn}'
HOSTNAME = '${fqdn}'
TASK_ERROR_EMAIL = '${task_error_email}'
DEBUG=${debug}


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '${db_name}',
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': None,
        'USER': '${db_username}',
        'PASSWORD': '${db_password}',
        'HOST': '${db_host}'
    }
}


EXPORT_STAGING_ROOT = '${exports_dir}/staging/'

# where exports are stored for public download
EXPORT_DOWNLOAD_ROOT = '${exports_dir}/download/'

# the root url for export downloads
EXPORT_MEDIA_ROOT = '/downloads/'

# home dir of the OSMAnd Map Creator
OSMAND_MAP_CREATOR_DIR = '${base_dir}/osmandmapcreator'

# location of the garmin config file
GARMIN_CONFIG = '${app_root}/utils/conf/garmin_config.xml'

OVERPASS_API_URL = '${overpass_api_url}'
EOF

cat <<EOF | sudo tee /etc/postfix/main.cf
# See /usr/share/postfix/main.cf.dist for a commented, more complete version


# Debian specific:  Specifying a file name will cause the first
# line of that file to be used as the name.  The Debian default
# is /etc/mailname.
#myorigin = /etc/mailname

smtpd_banner = $myhostname ESMTP $mail_name (Ubuntu)
biff = no

# appending .domain is the MUA's job.
append_dot_mydomain = no

# Uncomment the next line to generate "delayed mail" warnings
#delay_warning_time = 4h

readme_directory = no

# TLS parameters
smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
smtpd_use_tls=yes
smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache

# See /usr/share/doc/postfix/TLS_README.gz in the postfix-doc package for
# information on enabling SSL in the smtp client.

smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination
myhostname = ${hostname}
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
mydestination = ${hostname}, localhost.localdomain, localhost
relayhost =
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all
inet_protocols = ipv4
EOF

cat <<EOF > ${app_root}/utils/conf/garmin_config.xml
<?xml version="1.0" encoding="utf-8"?>
<!--
    Garmin IMG file creation config.
    @see utils/garmin.py
-->
<garmin obj="prog" src="export.hotosm.org">
    <mkgmap>${base_dir}/mkgmap/mkgmap.jar</mkgmap>
    <splitter>${base_dir}/splitter/splitter.jar</splitter>
    <xmx>1024m</xmx>
    <description>HOT Export Garmin Map</description>
    <family-name>HOT Exports</family-name>
    <family-id>2</family-id>
    <series-name>HOT Exports</series-name>
</garmin>
EOF

cat <<EOF > /etc/nginx/sites-available/osm-export-tool2
server {
  server_name ${fqdn};
  listen 0.0.0.0:80;

  location /static/ {
    alias ${app_root}/static/;
  }

  location /downloads/ {
    alias ${exports_dir};
  }

  location / {
    proxy_pass http://127.0.0.1:8001;
    proxy_set_header X-Forwarded-Host \$server_name;
    proxy_set_header X-Real-IP \$remote_addr;
  }
}
EOF

ln -sf /etc/nginx/sites-available/osm-export-tool2 /etc/nginx/sites-enabled/00-osm-export-tool2
rm -f /etc/nginx/sites-enabled/default

>&2 echo "Generating Upstart scripts..."

cat <<EOF > /etc/init/celery.conf
description     "celery"

start on (local-filesystems and net-device-up and runlevel [2345])
stop on shutdown

env DJANGO_SETTINGS_MODULE=core.settings.site

respawn
#respawn limit 5 60

pre-start script
    echo "[`date '+%c'`] Starting: celery" >> /var/log/celery.log
end script

pre-stop script
    echo "[`date '+%c'`] Stopping: celery" >> /var/log/celery.log
end script

exec start-stop-daemon \
        --start \
        --chdir ${app_root} \
        --chuid ubuntu \
        --make-pidfile \
        --pidfile /var/run/celery.pid \
                --exec /usr/local/bin/celery -- -A core worker >> /var/log/celery.log 2>&1
EOF

cat <<EOF > /etc/init/celery-beat.conf
description     "celery-beat"

start on (local-filesystems and net-device-up and runlevel [2345])
stop on shutdown

env DJANGO_SETTINGS_MODULE=core.settings.site

respawn
#respawn limit 5 60

pre-start script
    echo "[`date '+%c'`] Starting: celery-beat-beat" >> /var/log/celery-beat.log
end script

pre-stop script
    echo "[`date '+%c'`] Stopping: celery-beat-beat" >> /var/log/celery-beat.log
end script

exec start-stop-daemon \
        --start \
        --chdir ${app_root} \
        --chuid ubuntu \
        --make-pidfile \
        --pidfile /var/run/celery-beat.pid \
                --exec /usr/local/bin/celery -- -A core beat >> /var/log/celery-beat.log 2>&1
EOF

cat <<EOF > /etc/init/gunicorn.conf
description     "osm-export-tool2 (gunicorn)"

start on (local-filesystems and net-device-up and runlevel [2345])
stop on shutdown

env DJANGO_SETTINGS_MODULE=core.settings.site
env STATIC_ROOT=${app_root}/static

respawn
#respawn limit 5 60

pre-start script
    echo "[`date '+%c'`] Starting: osm-export-tool2" >> /var/log/osm-export-tool2.log
end script

pre-stop script
    echo "[`date '+%c'`] Stopping: osm-export-tool2" >> /var/log/osm-export-tool2.log
end script

exec start-stop-daemon \
        --start \
        --chdir ${app_root} \
        --chuid ubuntu \
        --make-pidfile \
        --pidfile /var/run/osm-export-tool2.pid \
        --exec /usr/local/bin/gunicorn -- core.wsgi:application --workers=3 --bind :8001 >> /var/log/osm-export-tool2.log 2>&1
EOF

>&2 echo "Configuring PostgreSQL..."

echo "CREATE ROLE ${db_username} WITH LOGIN PASSWORD '${db_password}' SUPERUSER INHERIT" | sudo -u postgres psql
sudo -u postgres createdb -O ${db_username} ${db_name}

>&2 echo "Initializing database..."

export DJANGO_SETTINGS_MODULE=core.settings.site

python manage.py migrate

>&2 echo "Generating static assets..."

python manage.py collectstatic --no-input

chown -R ubuntu ${app_root}
chown -R ubuntu ${exports_dir}

# # Commands to run in separate sessions:
#
# # ./manage.py runserver 0.0.0.0:8000
# # celery -A core worker
