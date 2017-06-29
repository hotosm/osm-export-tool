import os

class Artifact(object):
    def __init__(self,parts,format_name,theme=None,basename=None):
        self._parts = parts
        self._theme = theme
        self._format_name = format_name
        self._basename = basename

    @property
    def parts(self):
        return self._parts

    @property
    def format_name(self):
        return self._format_name

    @property
    def theme(self):
        return self._theme

    @property
    def basename(self):
        if len(self.parts) == 1:
            return self.parts[0]
        else:
            if self._basename:
                return self._basename
            else:
                raise Exception("Basename must be specified for multipart artifact")

    def __repr__(self):
        return "artifact: {0} {1} {2}".format(self._parts, self._theme, self._format_name)
