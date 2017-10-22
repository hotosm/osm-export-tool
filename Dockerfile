FROM quay.io/hotosm/osm-export-tool2-omimimage:latest as omim
# pull in reference for later COPY

FROM quay.io/hotosm/osm-export-tool2-baseimage:latest
LABEL maintainer "Seth Fitzsimmons <seth@mojodna.net>"

ENV DEBIAN_FRONTEND noninteractive

ENV GENERATOR_TOOL /usr/local/bin/generator_tool

# TODO set DATA= something, as generator_tool looks in __dirname/../../data
RUN mkdir -p /usr/data
COPY --from=omim /usr/local/src/omim/data/categories.txt /usr/data/
COPY --from=omim /usr/local/src/omim/data/classificator.txt /usr/data/
COPY --from=omim /usr/local/src/omim/data/countries.txt /usr/data/
COPY --from=omim /usr/local/src/omim/data/countries-strings /usr/data/countries-strings
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


COPY requirements.txt /opt/osm-export-tool2/
COPY requirements-dev.txt /opt/osm-export-tool2/

WORKDIR /opt/osm-export-tool2/

RUN pip install -U pip \
  && pip install -r requirements-dev.txt \
  && pip install gunicorn \
  && rm -rf /root/.cache

RUN yarn global add tl @mapbox/mbtiles @mapbox/tilejson tilelive-http

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
