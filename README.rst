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

.. code-block:: python

    from nldi_flowtools import *
    splitcatchment(-93,45,True)
    
This splitcatchment function returns the following response in GeoJson.    

.. code-block:: python

        {
          "outputs": [
            {
              "id": "nldi-splitcatchment-response",
              "value": {
                "type": "FeatureCollection",
                "features": [
                  {
                    "type": "Feature",
                    "id": "catchment",
                    "geometry": {
                      "type": "Polygon",
                      "coordinates": [
                        [
                          [
                            -93.0047,
                            44.9929
                          ],
                          [
                            -93.0053,
                            44.993
                          ],
                          [
                            -93.0051,
                            44.9944
                          ],
                          [
                            -93.0067,
                            44.9949
                          ],
                          [
                            -93.0091,
                            44.9959
                          ],
                          [
                            -93.01,
                            44.9974
                          ],
                          ...
                          [
                            -93.0047,
                            44.9929
                          ]
                        ]
                      ]
                    },
                    "properties": {
                      "catchmentID": "1100118"
                    }
                  },
                  {
                    "type": "Feature",
                    "id": "splitCatchment",
                    "geometry": {
                      "type": "Polygon",
                      "coordinates": [
                        [
                          [
                            -93.000192,
                            45.000058
                          ],
                          [
                            -93.000204,
                            44.999789
                          ],
                          [
                            -92.999442,
                            44.999772
                          ],
                          [
                            -92.99943,
                            45.000041
                          ],
                          [
                            -93.000192,
                            45.000058
                          ]
                        ]
                      ]
                    },
                    "properties": {}
                  }
                ]
              }
            }
          ]
        }

