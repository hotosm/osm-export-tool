FROM ubuntu:16.04
MAINTAINER Seth Fitzsimmons <seth@mojodna.net>

ENV DEBIAN_FRONTEND noninteractive

RUN \
  apt update \
  && apt upgrade -y \
  && apt install -y --no-install-recommends \
    apt-transport-https \
    curl \
    software-properties-common \
  && curl -sf https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
  && add-apt-repository -y -u -s "deb https://deb.nodesource.com/node_6.x $(lsb_release -c -s) main" \
  && add-apt-repository -y -u ppa:ubuntugis/ubuntugis-unstable \
  && apt install -y --no-install-recommends \
    libpq-dev \
    python-dev \
    python-pip \
    python-setuptools \
    python-wheel \
    gdal-bin \
    libgdal-dev \
    python-gdal \
    osmctools \
    spatialite-bin \
    libspatialite7 \
    libspatialite-dev \
    default-jre-headless \
    zip \
    unzip \
    libxslt1-dev \
    build-essential \
    git \
    libffi-dev \
    libmagic1 \
    libsqlite3-mod-spatialite \
    nodejs \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/osm-export-tool2/
COPY requirements-dev.txt /opt/osm-export-tool2/

WORKDIR /opt/osm-export-tool2/

RUN pip install -r requirements-dev.txt \
  && pip install gunicorn \
  && rm -rf /root/.cache

RUN \
  curl -sfL http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip -o /tmp/osmandmapcreator.zip \
    && unzip /tmp/osmandmapcreator.zip -d /opt/osmandmapcreator \
    && rm /tmp/osmandmapcreator.zip

RUN \
  curl -sfL http://www.mkgmap.org.uk/download/mkgmap-r3870.zip -o /tmp/mkgmap.zip \
    && unzip /tmp/mkgmap.zip -d /opt/mkgmap \
    && rm /tmp/mkgmap.zip

RUN \
  curl -sfL http://www.mkgmap.org.uk/download/splitter-r580.zip -o /tmp/splitter.zip \
    && unzip /tmp/splitter.zip -d /opt/splitter \
    && rm /tmp/splitter.zip

COPY ui/ /opt/osm-export-tool2/ui/

WORKDIR /opt/osm-export-tool2/ui/

RUN \
  npm install \
  && rm -rf /root/.npm \
  && npm run pack \
  && rm -rf node_modules/

COPY . /opt/osm-export-tool2/

RUN \
  mkdir -p /opt/export_staging /opt/export_downloads /opt/static \
  && useradd exports \
  && chown -R exports:exports /opt/export_staging /opt/export_downloads /opt/static /opt/osm-export-tool2

USER exports

WORKDIR /opt/osm-export-tool2/

RUN \
  python manage.py collectstatic --no-input

VOLUME ["/opt/export_staging", "/opt/export_downloads", "/opt/static"]

CMD ["echo", "Override this command"]
