import os

class Artifact(object):
    def __init__(self,parts,format_name,theme=None):
        self._parts = parts
        self._theme = theme
        self._format_name = format_name

    @property
    def parts(self):
        return self._parts

    @property
    def format_name(self):
        return self._format_name

    @property
    def theme(self):
        return self._theme

    def __repr__(self):
        return "artifact: {0} {1} {2}".format(self._parts, self._theme, self._format_name)
