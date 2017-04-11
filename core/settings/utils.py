# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))


def ABS_PATH(*args):
    return os.path.normpath(os.path.join(DJANGO_ROOT, *args))

