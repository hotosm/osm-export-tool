FROM ubuntu:16.04 as omim
WORKDIR /usr/local/src

RUN \
  apt update \
  && apt upgrade -y \
  && apt install -y build-essential git libsqlite3-dev qt5-default

RUN \
  git clone --recursive --depth 1 https://github.com/mapsme/omim.git

WORKDIR /usr/local/src/omim

RUN \
  echo | ./configure.sh \
  && CONFIG="gtool no-tests" tools/unix/build_omim.sh -cr

FROM ubuntu:16.04
LABEL maintainer "Seth Fitzsimmons <seth@mojodna.net>"

ENV DEBIAN_FRONTEND noninteractive

RUN \
  apt update \
  && apt upgrade -y \
  && apt install -y --no-install-recommends \
    apt-transport-https \
    curl \
    software-properties-common \
  && curl -sf https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
  && add-apt-repository -y -u "deb https://deb.nodesource.com/node_6.x $(lsb_release -c -s) main" \
  && add-apt-repository -y -u ppa:ubuntugis/ubuntugis-unstable \
  && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
  && add-apt-repository -y -u "deb https://dl.yarnpkg.com/debian/ stable main" \
  && apt install -y --no-install-recommends \
    build-essential \
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
    zip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV LC_ALL en_US.UTF-8

RUN \
  curl -sfL http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip -o /tmp/osmandmapcreator.zip \
    && unzip /tmp/osmandmapcreator.zip -d /opt/osmandmapcreator \
    && rm /tmp/osmandmapcreator.zip

RUN \
  curl -sfL https://s3.amazonaws.com/bdon/brandon.liu.hotosm.org/mkgmap-r3890.zip -o /tmp/mkgmap.zip \
    && unzip /tmp/mkgmap.zip -d /opt \
    && mv /opt/mkgmap-* /opt/mkgmap \
    && rm /tmp/mkgmap.zip

RUN \
  curl -sfL https://s3.amazonaws.com/bdon/brandon.liu.hotosm.org/splitter-r583.zip -o /tmp/splitter.zip \
    && unzip /tmp/splitter.zip -d /opt \
    && mv /opt/splitter-* /opt/splitter \
    && rm /tmp/splitter.zip

ENV GENERATOR_TOOL /usr/local/bin/generator_tool
ENV OSMCONVERT /usr/bin/osmconvert

# TODO set DATA= something, as generator_tool looks in __dirname/../../data
RUN mkdir -p /usr/data
COPY --from=omim /usr/local/src/omim/data/categories.txt /usr/data/
COPY --from=omim /usr/local/src/omim/data/classificator.txt /usr/data/
COPY --from=omim /usr/local/src/omim/data/countries.txt /usr/data/
COPY --from=omim /usr/local/src/omim/data/countries_meta.txt /usr/data/
COPY --from=omim /usr/local/src/omim/data/editor.config /usr/data/
COPY --from=omim /usr/local/src/omim/data/drules_proto.bin /usr/data/
COPY --from=omim /usr/local/src/omim/data/drules_proto_clear.bin /usr/data/
COPY --from=omim /usr/local/src/omim/data/drules_proto_dark.bin /usr/data/
COPY --from=omim /usr/local/src/omim/data/drules_proto_vehicle_clear.bin /usr/data/
COPY --from=omim /usr/local/src/omim/data/drules_proto_vehicle_dark.bin /usr/data/
COPY --from=omim /usr/local/src/omim/data/types.txt /usr/data/
COPY --from=omim /usr/local/src/omim/tools/unix/generate_mwm.sh /usr/local/bin/
COPY --from=omim /usr/local/src/omim-build-release/out/release/generator_tool /usr/local/bin/
# used to determine m_writableDir in Platform::Platform
COPY --from=omim /usr/local/src/omim/data/eula.html /usr/data/
COPY --from=omim /usr/lib/x86_64-linux-gnu/libQt5Network.so.5 /usr/lib/x86_64-linux-gnu/libQt5Network.so.5
