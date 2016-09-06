import os
from distutils.core import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="oet2",
    version="0.1",
    author="",
    author_email="",
    description="OSM Export Tool 2",
    long_description=(read('README.md')),
    # Full list of classifiers can be found at:
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
    ],
    license="BSD",
    keywords="django mapproxy",
    url='https://github.com/hotosm/osm-export-tool2',
    packages=['oet2',],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ]
)
