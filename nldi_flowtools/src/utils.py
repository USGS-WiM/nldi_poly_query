# from re import U
from requests import get
from rasterio import open, features
import rasterio.mask
from pyflwdir import from_array
from pyproj import Geod, CRS, Transformer
from shapely.ops import transform, split, snap, unary_union
from shapely.geometry import shape, mapping, Point, GeometryCollection, LineString, MultiLineString, Polygon, MultiPoint, MultiPolygon
import json
import numpy as np
from math import isinf

# arguments
NLDI_URL = 'https://labs.waterdata.usgs.gov/api/nldi/linked-data/comid/'
NLDI_GEOSERVER_URL = 'https://labs.waterdata.usgs.gov/geoserver/wmadata/ows'
IN_FDR_COG = '/vsicurl/https://prod-is-usgs-sb-prod-publish.s3.amazonaws.com/5fe0d98dd34e30b9123eedb0/fdr.tif'


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

def get_local_catchment(x, y):
    """Perform point in polygon query to NLDI geoserver to get local catchment geometry"""

    print('requesting local catchment...')

    wkt_point = f"POINT({x} {y})" 
    cql_filter = f"INTERSECTS(the_geom, {wkt_point})" 

    payload = {
        'service': 'wfs',
        'version': '1.0.0',
        'request': 'GetFeature',
        'typeName': 'wmadata:catchmentsp',
        'outputFormat': 'application/json',
        'srsName': 'EPSG:4326',
        'CQL_FILTER': cql_filter
    }
 
    # request catchment geometry from point in polygon query from NLDI geoserver
    r = get(NLDI_GEOSERVER_URL, params=payload)
 
    resp = r.json()

    # get catchment id
    catchmentIdentifier = json.dumps(resp['features'][0]['properties']['featureid'])

    # get main catchment geometry polygon
    features = resp['features'][0]
    if len(features["geometry"]['coordinates']) > 1:    # If the catchment is multipoly (I know this is SUPER annoying)
        r = 0
        catchmentGeom = []
        while r < len(features["geometry"]['coordinates']):
            print('Multipolygon catchment found:', json.dumps(features['properties']['featureid']))
            catchmentGeom.append(Polygon(features["geometry"]['coordinates'][r][0]))
            r += 1
        catchmentGeom = MultiPolygon(catchmentGeom)
    else:       # Else, the catchment is a single polygon (as it should be)
        catchmentGeom = Polygon(features["geometry"]['coordinates'][0][0])

    print('got local catchment:', catchmentIdentifier)
    return catchmentIdentifier, catchmentGeom
# return catchmentIdentifier, catchmentGeom


def get_local_catchments(coords):
    """Perform polygon intersect query to NLDI geoserver to get local catchments"""
    # # coords should be in json, like this: "coordinates": [[102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]]
    
    ## If there are more than 237 points, the catchment query will not work
    # Convert coords to shapely geom
    if len(coords) > 237:
        p = Polygon(coords)
        poly = p.simplify(0.00135, preserve_topology=False)

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

    # request catchment geometry from point in polygon query from NLDI geoserver
    print('request: ', NLDI_GEOSERVER_URL, payload)
    r = get(NLDI_GEOSERVER_URL, params=payload)
    print('request_url:', r.url)
    resp = r.json()
    
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
    # print('catchmentIdentifiers: ', catchmentIdentifiers, 'catchmentGeoms: ', catchmentGeoms)
    m = MultiPolygon(catchmentGeoms)
    catchmentGeoms = m 
    
    return catchmentIdentifiers, catchmentGeoms
# return catchmentIdentifiers, catchmentGeoms


def get_local_flowline(catchmentIdentifier):
    """Request NDH Flowline from NLDI with Catchment ID"""

    cql_filter = f"comid={catchmentIdentifier}" 

    payload = {
        'service': 'wfs',
        'version': '2.0.0',
        'request': 'GetFeature',
        'typeName': 'wmadata:nhdflowline_network',
        'maxFeatures': '500',
        'outputFormat': 'application/json',
        'srsName': 'EPSG:4326',
        'CQL_FILTER': cql_filter
    }

    # request  flowline geometry from point in polygon query from NLDI geoserver
    r = get(NLDI_GEOSERVER_URL, params=payload)
    print('request payload:', payload)
    flowline = r.json()
    print('response:', flowline)
    print('got local flowline')

    # Convert the flowline to a geometry colelction to be exported
    nhdGeom = flowline['features'][0]['geometry']
    nhdFlowline = GeometryCollection([shape(nhdGeom)])[0]
    nhdFlowline = LineString([xy[0:2] for xy in list(nhdFlowline[0].coords)])  # Convert xyz to xy

    return flowline, nhdFlowline
# return flowline, nhdFlowline

def get_local_flowlines(catchmentIdentifiers, *dist):
    """Request NDH Flowlines from NLDI with Catchment ID"""
    # if not dist:
    #     dist = 0

    catchmentIdentifiers = tuple(catchmentIdentifiers)
    
    cql_filter = f"comid IN {catchmentIdentifiers}" 
    
    payload = {
        'service': 'wfs',
        'version': '2.0.0',
        'request': 'GetFeature',
        'typeName': 'wmadata:nhdflowline_network',
        'maxFeatures': '500',
        'outputFormat': 'application/json',
        'srsName': 'EPSG:4326',
        'CQL_FILTER': cql_filter
    }
    r = get(NLDI_GEOSERVER_URL, params=payload)
    flowlines = r.json()
    # print('r url;', r.url)
    print('got flowlines')

    # Convert the flowline to a geometry collection to be exported
    nhdGeom = [feature['geometry']['coordinates'][0] for feature in flowlines['features']]
    nhdFlowlines = MultiLineString(nhdGeom)

    
    fromnode_list = []
    tonode_list = {}
        # Convert the flowline to a geometry colelction to be exported
        
    for feature in flowlines['features']:
        fromnode_list.append(feature['properties']['fromnode'])
        tonode_list[feature['properties']['comid']] = feature['properties']['tonode']
    
    print('outputs:', fromnode_list, tonode_list)
    outlets = find_out_flowline(tonode_list, fromnode_list)

    if not dist:
        dist = 0

    if dist:
        payload = {'f': 'json', 'distance': dist}
        flowlines = {'type': 'FeatureCollection', 'features': []}
        downstream_geom = []
        for id in outlets:
            # request  flowline geometry from point in polygon query from NLDI geoserver
            r = get(NLDI_URL  + str(id) + '/navigation/DM/flowlines', params=payload)
            # cql_filter = f"comid={id}" 

            # payload = {
            #     'service': 'wfs',
            #     'version': '2.0.0',
            #     'request': 'GetFeature',
            #     'typeName': 'wmadata:nhdflowline_network',
            #     'maxFeatures': '500',
            #     'outputFormat': 'application/json',
            #     'srsName': 'EPSG:4326',
            #     'distance': dist,
            #     'CQL_FILTER': cql_filter
            # }
            # r = get(NLDI_GEOSERVER_URL, params=payload)
            flowline = r.json()
            print('r url;', r.url)
            downstream_geom.append(flowline['features'][0]['geometry']['coordinates'])
        # print('ndhGeom:', nhdGeom)
        downstreamFlowlines = MultiLineString(downstream_geom)
        nhdFlowlines = MultiLineString()
        print('got trace downstream flowline')

    return flowlines, nhdFlowlines
# return flowlines, nhdFlowline


def get_total_basin(catchmentIdentifier):
    """Use local catchment identifier to get local upstream basin geometry from NLDI"""

    print('getting upstream basin...')

    # request upstream basin
    payload = {'f': 'json', 'simplified': 'false'}

    # request upstream basin from NLDI using comid of catchment point is in
    r = get(NLDI_URL + catchmentIdentifier + '/basin', params=payload)

    resp = r.json()

    # convert geojson to ogr geom
    features = resp['features']
    totalBasinGeom = GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])

    print('finished getting upstream basin')
    return totalBasinGeom
# return totalBasinGeom


def get_upstream_basin(catchment, totalBasinGeom):
    """Get upstream basin geometry by subtracting the local catchment from the totalBasinGeom"""

    d = 0.00045
    cf = 1.3  # cofactor

    upstreamBasinGeom = totalBasinGeom.symmetric_difference(catchment).buffer(-d).buffer(d*cf).simplify(d)
    return upstreamBasinGeom
# return upstreamBasinGeom


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


def get_coordsys():
    """Get coordinate system of input flow direction raster"""

    with open(IN_FDR_COG, 'r') as ds:
        # get raster crs
        dest_crs = ds.crs

        # create wgs84 crs
        wgs84 = CRS('EPSG:4326')

        # check to see if raster is already wgs84
        # latlon = dest_crs == wgs84

        transformToRaster = Transformer.from_crs(wgs84, dest_crs, always_xy=True).transform
        transformToWGS84 = Transformer.from_crs(dest_crs, wgs84, always_xy=True).transform

    return transformToRaster, transformToWGS84
# return transformToRaster, transformToWGS84


def project_point(x, y, transformToRaster):
    """Project point to flow direction raster crs"""

    point_geom = Point(x, y)
    print('original point:', point_geom)

    projected_point = transform_geom(transformToRaster, point_geom)
    print('projected point:', projected_point)

    projected_xy = projected_point.coords[:][0]

    # Test if one of the project point coordinates is infinity. If this is the case
    # then the point was not properly projected to the CRS of the DEM. This has happened
    # when proj version is greater than 6.2.1
    projected_x = projected_point.coords[:][0][0]
    if isinf(projected_x) is True:
        print('Input point was not properly projected. Check PROJ version, must be 6.2.1. Quiting program.')
        exit()

    return projected_xy
# return  projected_xy


def get_flowgrid(catchment_geom, transformToRaster):
    """Use a 90 meter buffer of the local catchment to clip NHD Plus v2 flow direction raster"""

    print('start clip raster')
    with open(IN_FDR_COG, 'r') as ds:

        # get raster crs
        dest_crs = ds.crs

        # create wgs84 crs
        wgs84 = CRS('EPSG:4326')

        # check to see if raster is already wgs84
        latlon = dest_crs == wgs84

        # transform catchment geometry to use for clip
        projected_catchment_geom = transform_geom(transformToRaster, catchment_geom)

        # buffer catchment geometry by 90m before clipping flow direction raster
        buffer_projected_catchment_geom = GeometryCollection([projected_catchment_geom.buffer(90)])

        # clip input fd
        flwdir, flwdir_transform = rasterio.mask.mask(ds, buffer_projected_catchment_geom, crop=True)  
        print('finish clip raster')

    # import clipped fdr into pyflwdir
    flw = from_array(flwdir[0], ftype='d8', transform=flwdir_transform, latlon=latlon)
    
    return flw, flwdir_transform
# return flw, flwdir_transform


def split_catchment(catchment_geom, projected_xy, transformToRaster, transformToWGS84):
    """Produce split catchment delienation from X,Y"""

    print('start split catchment...')

    with open(IN_FDR_COG, 'r') as ds:
        profile = ds.profile

        # print fdr value at click point
        for val in ds.sample([projected_xy]): 
            print('FDR Value at Click Point:', val)

        # get raster crs
        dest_crs = ds.crs

        # create wgs84 crs
        wgs84 = CRS('EPSG:4326')

        # check to see if raster is already wgs84
        latlon = dest_crs == wgs84

        # transform catchment geometry to use for clip
        projected_catchment_geom = transform_geom(transformToRaster, catchment_geom)

        # buffer catchment geometry by 0m before clipping flow direction raster
        buffer_projected_catchment_geom = GeometryCollection([projected_catchment_geom.buffer(0)])

        # clip input fd
        flwdir, flwdir_transform = rasterio.mask.mask(ds, buffer_projected_catchment_geom, crop=True)
        print('finish clip raster')

    # import clipped fdr into pyflwdir
    flw = from_array(flwdir[0], ftype='d8', transform=flwdir_transform, latlon=latlon)

    # used for snapping click point
    stream_order = flw.stream_order()
    print('Calculated Stream Order')

    # delineate subbasins
    subbasins = flw.basins(xy=projected_xy, streams=stream_order>1)   # streams=stream_order>4

    # convert subbasins from uint32
    subbasins = subbasins.astype(np.int32)

    # convert raster to features
    mask = subbasins != 0
    polys = features.shapes(subbasins, transform=flwdir_transform, mask=mask)

    # just get one we want [not sure why we need to grab this]
    poly = next(polys)

    # project back to wgs84
    split_geom = transform(transformToWGS84, shape(poly[0]))

    print('finish split catchment.')
    return split_geom
# return split_geom


def get_onFlowline(projected_xy, flowline, transformToRaster):
    """Determine if x,y is on a NHD Flowline (within 15m)"""

    linestringlist = []
    for pair in flowline['features'][0]['geometry']['coordinates'][0]:
        linestringlist.append((pair[0], pair[1]))

    linestring = LineString(linestringlist)

    # Project the flowline to the same crs as the flw raster
    projectedNHD = transform_geom(transformToRaster, linestring)

    # What is the distance from the Click Point to the NHD Flowline?
    clickPnt = Point(projected_xy)
    clickDist = clickPnt.distance(projectedNHD)

    # Is the Click Point on a flowline?
    if clickDist < 15:
        print('Clickpoint is on a NHD Flowline')
        onFlowline = True

    else:
        print('Clickpoint is NOT on a NHD Flowline')
        onFlowline = False

    return onFlowline
# return onFlowline


def get_raindropPath(flw, projected_xy, nhdFlowline, flowline, transformToRaster, transformToWGS84):

    # Convert the flowline to a linestring
    linestringlist = []
    for pair in flowline['features'][0]['geometry']['coordinates'][0]:
        linestringlist.append((pair[0], pair[1]))

    linestring = LineString(linestringlist)

    # Project the flowline to the same crs as the flw raster
    projectedNHD = transform_geom(transformToRaster, linestring)  # dfNHD.geometry[0][0]

    # Convert the flowline coordinates to a format that can be iterated
    line = list(projectedNHD.coords)
    print('created list of nhd coords  ')

    # Loop thru the flowline coordinates, grab the xy coordinantes and put them in separate lists.
    # Use these lists in the index function of pyflwdir to grap the ids of the cell in which these points fall
    # lastID = len(line) - 1
    xlist = []
    ylist = []
    nhdCellList = []
    for i in line:
        # if i == line[-1]:    # Pass the last point in the flowline. Sometimes this point is outside of
        #      pass                 # the flw raster and this will cause flw.index() to fail.
        # if i != line[-1]:
        # print(i)
        xlist = (i[0])
        ylist = (i[1])
        cellIndex = flw.index(xlist, ylist)
        nhdCellList.append(cellIndex)
    print('nhd converted to raster  ')

    # create mask from in the same of the flw raster
    nhdMask = np.zeros(flw.shape, dtype=bool)

    # Set the flowline cells to true
    nhdMask.flat[nhdCellList] = True

    # trace downstream
    path, dist = flw.path(
        xy=projected_xy,
        mask=nhdMask
        )

    # get points on raindropPath
    pathPoints = flw.xy(path)

    # loop thru the downstream path points and create a dict of coords
    lastPointID = pathPoints[0][0].size - 1
    i = 0
    coordlist = {'type': 'LineString', 'coordinates': []}
    while i <= lastPointID:
        x = pathPoints[0][0][i]
        y = pathPoints[1][0][i]
        coordlist['coordinates'].append([x, y])
        i += 1

    if len(coordlist['coordinates']) < 2:
        print('Failed to trace raindrop path! Try another point. ')
    if len(coordlist['coordinates']) >= 2:
        print('traced raindrop path   ')

    # Convert the dict of coords to ogr geom
    pathGeom = GeometryCollection([shape(coordlist)])

    # Project the ogr geom to WGS84
    projectedPathGeom = transform(transformToWGS84, pathGeom)

    # Snap raindropPath points to the flowline within a ~35m buffer
    snapPath = snap(projectedPathGeom[0], nhdFlowline, .00045)

    # Convert snapPath to a geometry collection
    snapPath = GeometryCollection([snapPath])

    # Grap all the points of intersection between the raindropPath and the flowline
    intersectionpoints = nhdFlowline.intersection(snapPath)

    # Filter the intersecting points by geometry type. The downstream path
    # will then be split by each point in the intersectionpoints geom.
    if type(intersectionpoints) == MultiPoint:
        for i in intersectionpoints:
            splitPoint = snap(Point(i.coords), snapPath, .0002)
            snapPath = split(snapPath[0], splitPoint)
    if type(intersectionpoints) == LineString:
        for i in intersectionpoints.coords:
            splitPoint = snap(Point(i), snapPath, .0002)
            snapPath = split(snapPath[0], splitPoint)
    if type(intersectionpoints) == Point:
        splitPoint = snap(intersectionpoints, snapPath, .0002)
        snapPath = split(snapPath[0], splitPoint)
    if type(intersectionpoints) == MultiLineString or type(intersectionpoints) == GeometryCollection:
        for i in intersectionpoints:
            for j in i.coords:
                splitPoint = snap(Point(j), snapPath, .0002)
                snapPath = split(snapPath[0], splitPoint)

    # The first linestring in the snapPath geometry collection in the raindropPath
    raindropPath = snapPath[0]

    return raindropPath
# return raindropPath


def get_intersectionPoint(x, y, onFlowline, *raindropPath):
    """Return the intersection point between the NHD Flowline and the raindropPath"""

    if onFlowline is True:
        intersectionPoint = Point(x, y)

    if onFlowline is False:
        raindropPath = raindropPath[0]  # raindropPath is returned as a tuple, reset it to the first part of the tuple
        # The last point on the raindropPath is the intersectionPoint
        coordID = len(raindropPath.coords) - 1
        intersectionPoint = Point(raindropPath.coords[coordID][0], raindropPath.coords[coordID][1])  # The first two coords of the point are used incase the point has a Z value
        print('found intersection point')

    return intersectionPoint
# return intersectionPoint


def get_reachMeasure(intersectionPoint, flowline, *raindropPath):
    """Collect NHD Flowline Reach Code and Measure"""
    print('intersectionPoint: ',  intersectionPoint)

    # Set Geoid to measure distances in meters
    geod = Geod(ellps="WGS84")

    # Convert the flowline to a geometry colelction to be exported
    nhdGeom = flowline['features'][0]['geometry']
    nhdFlowline = GeometryCollection([shape(nhdGeom)])[0]

    # Select the stream name from the NHD Flowline
    streamname = flowline['features'][0]['properties']['gnis_name']
    if streamname == ' ':
        streamname = 'none'

    # Create streamInfo dict and add some data
    streamInfo = {'gnis_name': streamname,
                  'comid': flowline['features'][0]['properties']['comid'],  # 'lengthkm': flowline['features'][0]['properties']['lengthkm'],
                  'intersectionPoint': (intersectionPoint.coords[0][1], intersectionPoint.coords[0][0]),
                  'reachcode': flowline['features'][0]['properties']['reachcode']}

    # Add more data to the streamInfo dict
    if raindropPath:
        streamInfo['raindropPathDist'] = round(geod.geometry_length(raindropPath[0]), 2)

    # If the intersectionPoint is on the NHD Flowline, split the flowline at the point
    if nhdFlowline.intersects(intersectionPoint) is True:
        NHDFlowlinesCut = split(nhdFlowline, intersectionPoint)

    # If they don't intersect (weird right?), buffer the intersectionPoint and then split the flowline
    if nhdFlowline.intersects(intersectionPoint) is False:
        buffDist = intersectionPoint.distance(nhdFlowline) * 1.01
        buffIntersectionPoint = intersectionPoint.buffer(buffDist)
        NHDFlowlinesCut = split(nhdFlowline, buffIntersectionPoint)

    # If the NHD Flowline was split, then calculate measure
    try:
        NHDFlowlinesCut[1]
    except AssertionError as error:  # If NHDFlowline was not split, then the intersectionPoint is either the first or last point on the NHDFlowline
        startPoint = Point(nhdFlowline[0].coords[0][0], nhdFlowline[0].coords[0][1])
        lastPointID = len(nhdFlowline[0].coords) - 1
        lastPoint = Point(nhdFlowline[0].coords[lastPointID][0], nhdFlowline[0].coords[lastPointID][1])
        if(intersectionPoint == startPoint):
            streamInfo['measure'] = 100
            error = 'The point of intersection is the first point on the NHD Flowline.'
        if(intersectionPoint == lastPoint):
            streamInfo['measure'] = 0
            error = 'The point of intersection is the last point on the NHD Flowline.'
        if(intersectionPoint != startPoint and intersectionPoint != lastPoint):
            error = 'Error: NHD Flowline measure not calculated'
            streamInfo['measure'] = 'null'
        print(error)
    else:
        lastLineID = len(NHDFlowlinesCut) - 1
        distToOutlet = round(geod.geometry_length(NHDFlowlinesCut[lastLineID]), 2)
        flowlineLength = round(geod.geometry_length(nhdFlowline), 2)
        streamInfo['measure'] = round((distToOutlet/flowlineLength) * 100, 2)
    print('calculated measure and reach')

    return streamInfo
# return streamInfo


def split_flowline(intersectionPoint, flowline):

    # Convert the flowline to a geometry colelction to be exported
    nhdGeom = flowline['features'][0]['geometry']
    nhdFlowline = GeometryCollection([shape(nhdGeom)])[0]
    nhdFlowline = LineString([xy[0:2] for xy in list(nhdFlowline[0].coords)])  # Convert xyz to xy

    # If the intersectionPoint is on the NHD Flowline, split the flowline at the point
    if nhdFlowline.intersects(intersectionPoint) is True:
        NHDFlowlinesCut = split(nhdFlowline, intersectionPoint)

    # If they don't intersect (weird right?), buffer the intersectionPoint and then split the flowline
    if nhdFlowline.intersects(intersectionPoint) is False:
        buffDist = intersectionPoint.distance(nhdFlowline) * 1.01
        buffIntersectionPoint = intersectionPoint.buffer(buffDist)
        NHDFlowlinesCut = split(nhdFlowline, buffIntersectionPoint)

    # If the NHD Flowline was split, then calculate measure
    try:
        NHDFlowlinesCut[1]
    except AssertionError as error:  # If NHDFlowline was not split, then the intersectionPoint is either the first or last point on the NHDFlowline
        startPoint = Point(nhdFlowline[0].coords[0][0], nhdFlowline[0].coords[0][1])
        lastPointID = len(nhdFlowline[0].coords) - 1
        lastPoint = Point(nhdFlowline[0].coords[lastPointID][0], nhdFlowline[0].coords[lastPointID][1])
        if(intersectionPoint == startPoint):
            upstreamFlowline = GeometryCollection()
            downstreamFlowline = NHDFlowlinesCut
            error = 'The point of intersection is the first point on the NHD Flowline.'
        if(intersectionPoint == lastPoint):
            downstreamFlowline = GeometryCollection()
            upstreamFlowline = NHDFlowlinesCut
            error = 'The point of intersection is the last point on the NHD Flowline.'
        if(intersectionPoint != startPoint and intersectionPoint != lastPoint):
            error = 'Error: NHD Flowline measure not calculated'
            downstreamFlowline = GeometryCollection()
            upstreamFlowline = GeometryCollection()
        print(error)
    else:
        lastLineID = len(NHDFlowlinesCut) - 1
        upstreamFlowline = NHDFlowlinesCut[0]
        downstreamFlowline = NHDFlowlinesCut[lastLineID]
    print('split NHD Flowline')

    return upstreamFlowline, downstreamFlowline
# return upstreamFlowline, downstreamFlowline


def merge_downstreamPath(raindropPath, downstreamFlowline):
    """Merge downstreamFlowline and raindropPath"""

    # Pull out coords, place in a list and convert to a Linestring
    # This ensures that the returned geometry is a single Linestring and not a Multilinestring
    lines = MultiLineString([raindropPath, downstreamFlowline])
    outcoords = [list(i.coords) for i in lines]
    downstreamPath = LineString([i for sublist in outcoords for i in sublist])
    return downstreamPath
# return downstreamPath

def find_out_flowline(tonode_list, fromnode_list):
    # Find all the flowlines that are outlets from the poly_query
    outlet_flowlines = []
    for key in tonode_list:
        if not int(tonode_list[key]) in fromnode_list:
            # print(key, ' is an outlet flowline!')
            outlet_flowlines.append(int(key))
            print('There are ', len(outlet_flowlines), ' outlet flowlines.', outlet_flowlines)
    
    outlet_flowlines = tuple(outlet_flowlines)
    return outlet_flowlines
        
