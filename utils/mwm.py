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


class MWM(object):
    name = 'mwm'
    description = 'maps.me MWM'
    cmd = Template('generate_mwm.sh $input')

    def __init__(self, input):
        """
        Initialize the MWM generation utility.

        Args:
            pbf: the source PBF
        """
        self.input = input
        self.output = os.path.splitext(input)[0] + '.mwm'

    def run(self):
        if self.is_complete:
            LOG.debug("Skipping MWM, file exists")
            return

        convert_cmd = self.cmd.safe_substitute({
            'input': self.input,
        })

        LOG.debug('Running: %s' % convert_cmd)

        tmpdir = tempfile.mkdtemp()
        env = os.environ.copy()
        env.update(MWM_WRITABLE_DIR=tmpdir, TARGET=os.path.dirname(self.output))

        try:
            subprocess.check_call(
                convert_cmd,
                env=env,
                shell=True,
                executable='/bin/bash',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            LOG.debug('generate_mwm.sh complete')
        finally:
            shutil.rmtree(tmpdir)

    @property
    def results(self):
        return [Artifact([self.output], self.name)]

    @property
    def is_complete(self):
        return os.path.isfile(self.output)
