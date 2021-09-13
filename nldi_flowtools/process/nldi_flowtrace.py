import logging
import time
from distutils.util import strtobool

from nldi_flowtools.src.flowtrace import Flowtrace
from pygeoapi.process.base import BaseProcessor

LOGGER = logging.getLogger(__name__)

PROCESS_METADATA = {
    "version": "0.1.0",
    "id": "nldi-flowtrace",
    "title": "NLDI Flow Trace process",
    "description": "NLDI Flow Trace process",
    "keywords": ["NLDI Flow Trace"],
    "links": [
        {
            "type": "text/html",
            "rel": "canonical",
            "title": "information",
            "href": "https://example.org/process",
            "hreflang": "en-US",
        }
    ],
    "inputs": [
        {
            "id": "lat",
            "title": "lat",
            "abstract": "The latitude coordinate of the pour point in decimal degrees",
            "input": {
                "literalDataDomain": {
                    "dataType": "float",
                    "valueDefinition": {"anyValue": True},
                }
            },
            "minOccurs": 1,
            "maxOccurs": 1,
        },
        {
            "id": "lon",
            "title": "lon",
            "abstract": "The longitude coordinate of the pour point in decimal degrees",
            "input": {
                "literalDataDomain": {
                    "dataType": "float",
                    "valueDefinition": {"anyValue": True},
                }
            },
            "minOccurs": 1,
            "maxOccurs": 1,
        },
        {
            "id": "raindroptrace",
            "title": "raindroptrace",
            "abstract": "If True, the raindropPath will be return. If False, it will not.",
            "input": {
                "literalDataDomain": {
                    "dataType": "boolean",
                    "valueDefinition": {"anyValue": True},
                }
            },
            "minOccurs": 1,
            "maxOccurs": 1,
        },
        {
            "id": "direction",
            "title": "direction",
            "abstract": 'This variable determines which portion of the NHD flowline will be returned. "up" returns the portion of the flowline that is upstream from the intersection between the raindropPath and the flowline. "down" returns the downstream portion of the flowline from the intersection point. And "none" returns the entire flowline.',
            "input": {
                "literalDataDomain": {
                    "dataType": "string",
                    "allowedValues": ["up", "down", "none"],
                    "defaultValue": "none",
                }
            },
            "minOccurs": 1,
            "maxOccurs": 1,
        },
    ],
    "outputs": [
        {
            "id": "upstreamFlowline",
            "title": "upstreamFlowline",
            "description": 'The portion of the NHD flowline upstream from the intersection point. This line will only be returned in the variable direction is set to "up".',
            "output": {"formats": [{"mimeType": "application/geo+json"}]},
        },
        {
            "id": "downstreamFlowline",
            "title": "downstreamFlowline",
            "description": 'The portion of the NHD flowline downstream from the intersection point. This line will only be returned in the variable direction is set to "down".',
            "output": {"formats": [{"mimeType": "application/geo+json"}]},
        },
        {
            "id": "nhdFlowline",
            "title": "nhdFlowline",
            "description": 'This is the entire NHD flowline that the raindropPath intersects with. This line will only be returned in the variable direction is set to "none".',
            "output": {"formats": [{"mimeType": "application/geo+json"}]},
        },
        {
            "id": "raindropPath",
            "title": "raindropPath",
            "description": 'This is the path that water will follow from the input point to the nearest NHD flowline. This line will only be returned if "raindropTrace" is set to True and the input point does not fall on an NHD flowline.',
            "output": {"formats": [{"mimeType": "application/geo+json"}]},
        },
    ],
    "example": {
        "inputs": [
            {"id": "lat", "value": "43.29139", "type": "text/plain"},
            {"id": "lon", "value": "-73.82705", "type": "text/plain"},
            {"id": "raindroptrace", "value": "False", "type": "text/plain"},
            {"id": "direction", "value": "none", "type": "text/plain"},
        ]
    },
}


class NLDIFlowtraceProcessor(BaseProcessor):
    """NLDI Split Catchment Processor"""

    def __init__(self, provider_def):
        """
        Initialize object
        :param provider_def: provider definition
        :returns: pygeoapi.process.nldi_delineate.NLDIDelineateProcessor
        """

        BaseProcessor.__init__(self, provider_def, PROCESS_METADATA)

    def execute(self, data):

        mimetype = "application/json"
        lat = float(data["lat"])
        lon = float(data["lon"])
        raindroptrace = bool(strtobool(data["raindroptrace"]))
        direction = data["direction"]

        print(lat, lon)

        timeBefore = time.perf_counter()

        results = Flowtrace(lon, lat, raindroptrace, direction)

        timeAfter = time.perf_counter()
        totalTime = timeAfter - timeBefore
        print("Total Time:", totalTime)

        # outputs = [{
        #     'results': results.serialize()
        # }]

        return mimetype, results.serialize()

    def __repr__(self):
        return "<NLDIFlowtraceProcessor> {}".format(self.nldi - flowtrace - response)