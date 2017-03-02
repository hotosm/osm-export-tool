#!/usr/bin/env bash

set -eo pipefail

sudo apt install -y python-pip
sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main"
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-9.6-postgis-2.3
sudo apt install libpq-dev python-dev

sudo -u postgres createuser -s -P hot
sudo -u postgres createdb -O hot hot_exports_dev

sudo apt-get install gdal-bin libgdal-dev python-gdal
sudo apt-get install osmctools
sudo apt-get install spatialite-bin libspatialite5 libspatialite-dev
sudo apt-get install default-jre zip unzip
sudo apt-get install rabbitmq-server
sudo apt install git
git clone git@github.com:hotosm/osm-export-tool2.git
cd osm-export-tool2/

sudo apt-get install libxslt1-dev

sudo pip install -r requirements-dev.txt

sudo apt install postfix

mkdir ~/exports

cat <<EOF > core/settings/site.py
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .prod import *  # NOQA

ALLOWED_HOSTS = ['10.0.1.56']
SESSION_COOKIE_DOMAIN = '10.0.1.56'
HOSTNAME = '10.0.1.56'
TASK_ERROR_EMAIL = 'seth@mojodna.net'
DEBUG=True


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'hot_exports_dev',
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': None,
        'USER': 'hot',
        'PASSWORD': 'hot',
        'HOST': 'localhost'
    }
}


EXPORT_STAGING_ROOT = '/home/ubuntu/exports/staging/'

# where exports are stored for public download
EXPORT_DOWNLOAD_ROOT = '/home/ubuntu/exports/download/'

# the root url for export downloads
EXPORT_MEDIA_ROOT = '/downloads/'

# home dir of the OSMAnd Map Creator
OSMAND_MAP_CREATOR_DIR = '/home/ubuntu/osmandmapcreator'

# location of the garmin config file
GARMIN_CONFIG = '/home/ubuntu/osm-export-tool2/utils/conf/garmin_config.xml'

OVERPASS_API_URL = 'http://overpass-api.de/api/interpreter'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join('/home/ubuntu/osm-export-tool2', 'static')
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
myhostname = osm-export-tool2
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
mydestination = osm-export-tool2, localhost.localdomain, , localhost
relayhost =
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all
inet_protocols = ipv4
EOF

export DJANGO_SETTINGS_MODULE=core.settings.site

python manage.py migrate
python manage.py collectstatic

# Commands to run in separate sessions:

# ./manage.py runserver 0.0.0.0:8000
# celery -A core worker
