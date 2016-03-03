# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging
import os
import subprocess
from string import Template

logger = logging.getLogger(__name__)


class BZ2Compressor(object):
    """
    Compress files.
    """

    def __init__(self, input=None, output=None, debug=False):
        """
        Initialize the compressor.

        Args:
            input: the file to compress
            output: the output file
        """
        if input is None:
            raise RuntimeError("Input filename is required.")

        if not os.path.exists(input):
            raise IOError('Cannot find input file for this task: {0}'.format(input))

        self.input = input

        if output:
            self.output = output
        else:
            # create output path from input path.
            self.output = '{0}.bz2'.format(self.input)

        self.debug = debug
        self.cmd = Template('bzip2 -c $input > $output')

    def compress(self, ):
        """
        Compress
        """
        convert_cmd = self.cmd.safe_substitute({'input': self.input, 'output': self.output})
        if(self.debug):
            print 'Running: %s' % convert_cmd
        proc = subprocess.Popen(convert_cmd, shell=True, executable='/bin/bash', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        returncode = proc.wait()
        if (returncode != 0):
            logger.error('%s', stderr)
            raise Exception, "bzip2 failed with return code: {0}".format(returncode)
        if(self.debug):
            print 'bzip2 returned: %s' % returncode
        return self.output
