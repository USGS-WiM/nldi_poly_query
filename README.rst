===============
NLDI Flow Tools
===============

.. image:: https://img.shields.io/travis/Anders-Hopkins/nldi_flowtools.svg
        :target: https://travis-ci.org/Anders-Hopkins/nldi_flowtools

.. image:: https://img.shields.io/pypi/v/nldi_flowtools.svg
        :target: https://pypi.python.org/pypi/nldi_flowtools


NLDI Flow Tools pulls from the NHD to delineate water flow paths and drainage basins from a lon, lat point.

* Free software: 3-clause BSD license
* Documentation: https://nldi-flowtools.readthedocs.io/

Install
------
* conda create -n env_name -c conda-forge python=3.8 gdal rasterio proj=6.2.1
* conda activate env_name
* pip install git+https://github.com/ACWI-SSWD/nldi_flowtools.git

Features
--------

* Splitcatchment delineates drainage basins from an input pour point.
* Flowtrace traces the flowpath of water from an input point to the nearest stream.

Useage
------
* from nldi_flowtools import *
* splitcatchment(-93,45,True)
* flowtrace(-93,45,True,'down')

