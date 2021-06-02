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

To find the catchment from a lon, lat point, use the splitcatchment() function. The first two inputs are the inputs are the longitude and latitude coordinates passed in as floats. The third input is the 'upstream' variable, which is passed as a boolean. If this is set to True, and the input point lands on an NHD Flowline, then the function will return both the local catchment geometry, and the 'mergedcatchment' geometry (the splitcatchment merged with all upstream catchments).

.. code-block:: python

    from nldi_flowtools import *
    splitcatchment(-93.02933761928982, 41.79037842455216, True)
    
This splitcatchment function returns the following response in GeoJson.    
        
.. image:: https://octodex.github.com/images/yaktocat.png) 

However, if the input point does not intersect an NHD Flowline, or if 'upstream' is set to False, then the local catchment and the splitcatchment geometries will be returned.

.. code-block:: python
