FROM quay.io/hotosm/osm-export-tool2-baseimage:latest
LABEL maintainer "Seth Fitzsimmons <seth@mojodna.net>"

ENV DEBIAN_FRONTEND noninteractive


COPY requirements.txt /opt/osm-export-tool2/
COPY requirements-dev.txt /opt/osm-export-tool2/

WORKDIR /opt/osm-export-tool2/

RUN pip install -r requirements-dev.txt \
  && pip install gunicorn \
  && rm -rf /root/.cache

RUN yarn global add tl @mapbox/mbtiles @mapbox/tilelive @mapbox/tilejson tilelive-http

COPY ui/ /opt/osm-export-tool2/ui/

WORKDIR /opt/osm-export-tool2/ui/

RUN \
  yarn \
  && rm -rf /root/.cache/yarn \
  && yarn run dist \
  && rm -rf node_modules/

COPY . /opt/osm-export-tool2/

RUN \
  mkdir -p /opt/export_staging /opt/export_downloads /opt/static \
  && useradd exports \
  && chown -R exports:exports /opt/export_staging /opt/export_downloads /opt/static /opt/osm-export-tool2

USER exports

WORKDIR /opt/osm-export-tool2/

RUN \
  python manage.py collectstatic --no-input --link \
  && python manage.py collectstatic -i ui\* --no-input \
  && mkdir /opt/static/css \
  && touch /opt/static/css/style.css

VOLUME ["/opt/export_staging", "/opt/export_downloads", "/opt/osm-export-tool2", "/opt/static"]

ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/osm-export-tool2/bin

CMD ["echo", "Override this command"]
