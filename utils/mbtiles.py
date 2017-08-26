# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import os
import shutil
import subprocess
import tempfile
from string import Template

from .artifact import Artifact

LOG = logging.getLogger(__name__)


class MBTiles(object):
    name = 'mbtiles'
    description = 'MBTiles archive'
    cmd = Template('generate_mwm.sh $input')
    cmd = Template(
        'tl copy -q -b "$bbox" -z $min_zoom -Z $max_zoom $source mbtiles://$output')

    def __init__(self, output, bbox, source, min_zoom, max_zoom):
        """
        Initialize the MBTiles generation utility.

        Args:
            output: the output archive
        """
        self.output = output
        self.bbox = bbox
        self.source = source
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom

    def run(self):
        if self.is_complete:
            LOG.debug("Skipping MBTiles, file exists")
            return

        convert_cmd = self.cmd.safe_substitute({
            'bbox': " ".join(map(str, self.bbox)),
            'min_zoom': self.min_zoom,
            'max_zoom': self.max_zoom,
            'source': self.source,
            'output': self.output,
        })

        LOG.debug('Running: %s' % convert_cmd)

        tmpdir = tempfile.mkdtemp()
        env = os.environ.copy()
        env.update(HOME=tmpdir, TARGET=os.path.dirname(self.output))

        try:
            subprocess.check_call(
                convert_cmd,
                env=env,
                shell=True,
                executable='/bin/bash',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            LOG.debug('MBTiles generation complete')
        finally:
            shutil.rmtree(tmpdir)

    @property
    def results(self):
        return [Artifact([self.output], self.name)]

    @property
    def is_complete(self):
        return os.path.isfile(self.output)
