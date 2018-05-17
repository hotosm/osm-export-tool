FROM ubuntu:trusty

# adapted from https://github.com/mediasuitenz/docker-overpass-api

# no tty
ARG DEBIAN_FRONTEND=noninteractive

ARG OSM_VER=0.7.54
ARG FCGI_CHILDREN=5
ENV EXEC_DIR=/srv/osm3s
ENV DB_DIR=/srv/osm3s/db

RUN build_deps="g++ make expat libexpat1-dev zlib1g-dev curl" \
  && set -x \
  && echo "#!/bin/sh\nexit 0" >/usr/sbin/policy-rc.d \
  && apt-get update \
  && apt-get install -y --force-yes --no-install-recommends \
       $build_deps \
       fcgiwrap \
       nginx \
       wget \
       vim \
       osmctools \
       ca-certificates \
  && rm /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default \
  && rm -rf /var/lib/apt/lists/* \
  && curl -sfo osm-3s_v$OSM_VER.tar.gz http://dev.overpass-api.de/releases/osm-3s_v$OSM_VER.tar.gz \
  && tar -zxvf osm-3s_v${OSM_VER}.tar.gz \
  && cd osm-3s_v* \
  && ./configure CXXFLAGS="-O2" --prefix="$EXEC_DIR" \
  && make -j $(nproc) install \
  && cd .. \
  && rm -rf osm-3s_v* \
  && apt-get purge -y --auto-remove $build_deps

RUN echo "FCGI_CHILDREN=${FCGI_CHILDREN}" > /etc/default/fcgiwrap

COPY nginx.conf /etc/nginx/nginx.conf
COPY docker-start /usr/local/sbin

CMD ["/usr/local/sbin/docker-start"]

EXPOSE 80
