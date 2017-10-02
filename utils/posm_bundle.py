# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import logging
import os
import tarfile

from django.utils.text import slugify

from .artifact import Artifact

LOG = logging.getLogger(__name__)


class POSMBundle(object):
    name = 'bundle'
    description = 'POSM Bundle'

    def __init__(self,
                 name,
                 description,
                 input_dir,
                 extent,
                 mbtiles_source=None,
                 mbtiles_minzoom=None,
                 mbtiles_maxzoom=None):
        self.name = name
        self.description = description
        self.input_dir = input_dir
        self.extent = extent
        self.mbtiles_source = mbtiles_source
        self.mbtiles_minzoom = mbtiles_minzoom
        self.mbtiles_maxzoom = mbtiles_maxzoom
        self.output = os.path.join(input_dir, "bundle.tar.gz")

    def run(self):
        if self.is_complete:
            LOG.debug("Skipping POSM bundle, file exists")
            return

        # assemble contents
        contents = {}
        prefix = slugify(self.name, allow_unicode=True)

        with tarfile.open(self.output, "w|gz") as bundle:
            for filename in os.listdir(self.input_dir):
                _, ext = os.path.splitext(filename)
                path = os.path.join(self.input_dir, filename)

                if ext == ".mbtiles":
                    target_filename = "tiles/{}.mbtiles".format(prefix)
                    contents[target_filename] = {
                        "type": "MBTiles",
                        "minzoom": self.mbtiles_minzoom,
                        "maxzoom": self.mbtiles_maxzoom,
                        "source": self.mbtiles_source,
                        "name": self.name,
                    }

                    bundle.add(path, target_filename)

                if ext == ".obf":
                    target_filename = "navigation/{}.obf".format(prefix)
                    contents[target_filename] = {
                        "type": "OsmAnd",
                    }

                    bundle.add(path, target_filename)

                if ext == ".mwm":
                    target_filename = "navigation/{}.mwm".format(prefix)
                    contents[target_filename] = {
                        "type": "Maps.me",
                    }

                    bundle.add(path, target_filename)

                if filename == "gmapsupp.img":
                    target_filename = "navigation/{}.img".format(prefix)
                    contents[target_filename] = {
                        "type": "Garmin IMG",
                    }

                    bundle.add(path, target_filename)

                if ext == ".gpkg":
                    target_filename = "data/{}.gpkg".format(prefix)
                    contents[target_filename] = {
                        "type": "Geopackage",
                    }

                    bundle.add(path, target_filename)

                if ext == ".kml":
                    target_filename = "data/{}.kml".format(prefix)
                    contents[target_filename] = {
                        "type": "KML",
                    }

                    bundle.add(path, target_filename)

                if filename == "unfiltered.pbf":
                    target_filename = "osm/{}.pbf".format(prefix)
                    contents[target_filename] = {
                        "type": "OSM/PBF",
                    }

                    bundle.add(path, target_filename)

            manifest = os.path.join(self.input_dir, "manifest.json")
            with open(manifest, "w") as m:
                json.dump({
                    "title": self.name,
                    "name": prefix,
                    "description": self.description,
                    "bbox": self.extent,
                    "content": contents,
                }, m)

            bundle.add(manifest, "manifest.json")

    @property
    def results(self):
        return [Artifact([self.output], self.name)]

    @property
    def is_complete(self):
        return os.path.isfile(self.output)
