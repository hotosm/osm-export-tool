# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    ))


def ABS_PATH(*args):
    return os.path.join(DJANGO_ROOT, *args)


def ensure_secret_key_file():
    """Checks that secret.py exists in settings dir. If not, creates one
with a random generated SECRET_KEY setting."""
    secret_path = ABS_PATH('core', 'settings', 'secret.py')
    if not os.path.exists(secret_path):
        from django.utils.crypto import get_random_string
        secret_key = get_random_string(
            50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
        with open(secret_path, 'w') as f:
            f.write("SECRET_KEY = " + repr(secret_key) + "\n")

# Import the secret key
ensure_secret_key_file()

SECRET_KEY = u'=7&iscku=1g2w89e0-^h!i5m@ud@#k89d^jaw(**t%llw__-&u'
