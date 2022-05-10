import json
import requests
from shapely.geometry import mapping, MultiLineString, Polygon, MultiPolygon
from shapely.ops import transform
import sys, random

# arguments
NLDI_URL = 'https://labs.waterdata.usgs.gov/api/nldi/linked-data/comid/'
NLDI_GEOSERVER_URL = 'https://labs.waterdata.usgs.gov/geoserver/wmadata/ows'


# functions
def geom_to_geojson(geom):
    """Return a geojson from an OGR geom object"""

    geojson_dict = mapping(geom)

    return geojson_dict
# return geojson_dict


def transform_geom(proj, geom):
    """Transform geometry"""

    projected_geom = transform(proj, geom)

    return projected_geom
# return projected_geom


def get_local_catchments(coords):
    """Perform polygon intersect query to NLDI geoserver to get local catchments"""
    
    ## If there are more than 237 points, the catchment query will not work
    # Convert coords to shapely geom
    if len(coords) > 237:
        poly = Polygon(coords).buffer(0)
        i = 0.000001
        while len(poly.exterior.coords) > 235:
            poly = poly.simplify(i, preserve_topology=True)
            i += 0.000001
        # while len(coords) > 235:
        #     coords.pop(random.randrange(len(coords)))
        # poly = Polygon(coords)

    else:
        poly = Polygon(coords)
    
    cql_filter = f"INTERSECTS(the_geom, {poly.wkt})"
    print('requesting local catchments...')     

    payload = {
        'service': 'wfs',
        'version': '1.0.0',
        'request': 'GetFeature',
        'typeName': 'wmadata:catchmentsp',
        'outputFormat': 'application/json',
        'srsName': 'EPSG:4326',
        'CQL_FILTER': cql_filter
    }

    # Try to request catchment geometry from polygon query from NLDI geoserver
    try:
        r = requests.get(NLDI_GEOSERVER_URL, params=payload)
        # Convert response to json
        resp = r.json()

    # If request fails or can't be converted to json, something's up
    except:
        if r.status_code == 200:
            print('Get local catchments request failed. Check to make sure query was submitted with lon, lat coords. Quiting nldi_flowtools query.')

        else:
            print('Quiting nldi_flowtools query. Error requesting catchment from Geoserver:', r.exceptions.HTTPError)

        # Kill program if request fails.
        sys.exit(1)

    features = resp['features']
    print('# of catchments', len(features)) 

    x = 0
    catchmentIdentifiers = []
    catchmentGeoms = []
    while x < len(features):    # Loop thru each catchment returned        
        catchmentIdentifiers.append(json.dumps(features[x]['properties']['featureid']))     # Add catchment IDs to list
        if len(features[x]["geometry"]['coordinates']) > 1:    # If the catchment is multipoly (I know this is SUPER annoying)
            r = 0
            while r < len(features[x]["geometry"]['coordinates']):
                print('Multipolygon catchment found:', json.dumps(features[x]['properties']['featureid']))
                catchmentGeoms.append(Polygon(features[x]["geometry"]['coordinates'][r][0]))
                r += 1
        else:       # Else, the catchment is a single polygon (as it should be)
            catchmentGeoms.append(Polygon(features[x]["geometry"]['coordinates'][0][0]))
        x += 1
    print('# of catchment geoms:', x )
    
    m = MultiPolygon(catchmentGeoms)
    catchmentGeoms = m 

    # Remove duplicates from list of catchment IDs
    catchmentIdentifiers = [x for x in catchmentIdentifiers if catchmentIdentifiers.count(x) == 1]

    
    return catchmentIdentifiers, catchmentGeoms
# return catchmentIdentifiers, catchmentGeoms


def get_local_flowlines(catchmentIdentifiers, dist):
    """Request NDH Flowlines from NLDI with Catchment ID"""

    print('# of catchment IDs:', len(catchmentIdentifiers))
    nhdGeom = []
    fromnode_list = []
    tonode_list = {}

    # Request catchments 100 or less at a time
    for i in range(0, len(catchmentIdentifiers), 101):
        chunk = catchmentIdentifiers[i:i + 101]
                
        catchmentids = tuple(chunk)

        cql_filter = f"comid IN {catchmentids}" 
        
        payload = {
            'service': 'wfs',
            'version': '1.0.0',
            'request': 'GetFeature',
            'typeName': 'wmadata:nhdflowline_network',
            'maxFeatures': '5000',
            'outputFormat': 'application/json',
            'srsName': 'EPSG:4326',
            'CQL_FILTER': cql_filter
        }

        # Try to request flowlines geometry from catchment ID from NLDI geoserver
        try:
            r = requests.get(NLDI_GEOSERVER_URL, params=payload)
            # Convert response to json
            flowlines = r.json()

        # If request fails or can't be converted to json, something's up
        except:
            if r.status_code == 200:
                print('Get local flowlines request failed. Check to make sure query was submitted with lon, lat coords. Quiting nldi_flowtools query.')

            else:
                print('Quiting nldi_flowtools query. Error requesting flowlines from Geoserver:', r.exceptions.HTTPError)

            # Kill program if request fails.
            sys.exit(1)

        print('got flowlines')

        for feature in flowlines['features']:
            # Get from and to nodes
            fromnode_list.append(feature['properties']['fromnode'])
            tonode_list[feature['properties']['comid']] = feature['properties']['tonode']
            # Convert the flowline to a geometry collection to be exported
            for coords in feature['geometry']['coordinates']:
                nhdGeom.append([coord[0:2] for coord in coords])

    outlets = find_out_flowline(tonode_list, fromnode_list)

    if not dist:
        flowlinesGeom = MultiLineString(nhdGeom)

    if dist:
        payload = {'f': 'json', 'distance': dist}

        flowlines = {'type': 'FeatureCollection', 'features': []}
        for id in outlets:
            # request downstream flowlines geometry NLDI
            try:
                r = requests.get(NLDI_URL  + str(id) + '/navigation/DM/flowlines', params=payload)
                downstreamflowlines = r.json()
                for feature in downstreamflowlines['features']:
                    nhdGeom.append(feature['geometry']['coordinates'])
            except:
                if r.status_code == 200:
                    print('Get local flowlines request failed. Check to make sure query was submitted with lon, lat coords. Quiting nldi_flowtools query.')

                else:
                    print('Quiting nldi_flowtools query. Error requesting flowlines from Geoserver:', r.exceptions.HTTPError)

                # Kill program if request fails.
                sys.exit(1)


        flowlinesGeom = MultiLineString(nhdGeom)
        print('got trace downstream flowline')

    return flowlines, downstreamflowlines, flowlinesGeom
    
# return flowlines, downstreamflowlines, flowlinesGeom


def merge_geometry(catchment, splitCatchment, upstreamBasin):
    """Attempt at merging geometries"""

    print('merging geometries...')
    d = 0.00045
    # d2 = 0.00015 # distance
    cf = 1.3  # cofactor

    splitCatchment = splitCatchment.simplify(d)

    diff = catchment.difference(splitCatchment).buffer(-d).buffer(d*cf).simplify(d)
    mergedCatchmentGeom = upstreamBasin.difference(diff).buffer(-d).buffer(d*cf).simplify(d)

    # mergedCatchmentGeom = upstreamBasin.union(splitCatchment).buffer(-d).buffer(d*cf).simplify(d)

    print('finished merging geometries')

    return mergedCatchmentGeom
# return mergedCatchmentGeom


def find_out_flowline(tonode_list, fromnode_list):
    # Find all the flowlines that are outlets from the poly_query
    outlet_flowlines = []
    for key in tonode_list:
        if not int(tonode_list[key]) in fromnode_list:
            outlet_flowlines.append(int(key))
    
    outlet_flowlines = tuple(outlet_flowlines)
    return outlet_flowlines
        
