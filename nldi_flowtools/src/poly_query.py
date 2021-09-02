from .utils import geom_to_geojson, get_local_catchment, get_local_flowlines, get_coordsys, \
    project_point, get_total_basin, split_catchment, get_onFlowline, get_upstream_basin, merge_geometry
import geojson
from shapely.ops import unary_union
from shapely.geometry import MultiPolygon

# catchmentGeom = None
# catchmentIDs = None
# totalBasinGeoms = []
# totalBasinGeom = None

def poly_Query(p_list):
    catchmentGeom = None
    catchmentIDs = None
    totalBasinGeoms = []
    totalBasinGeom = None
    flowlines = []
    nhdFlowlineGeom = []
    print('running poly_Query')
    print('p_list', p_list)

    ############# Get overlapping catchments #############
    catchmentIDs, catchmentGeom = get_local_catchment(p_list)
    catchment = geom_to_geojson(catchmentGeom)
    feature1 = geojson.Feature(geometry=catchment, id='catchment', properties={'catchmentID': catchmentIDs})
    
    ################ Get local flowlines #################
    for id in catchmentIDs:
        nhdFlowlineGeom.append(get_local_flowlines(id)[1])
        for geom in nhdFlowlineGeom:
            

    nhdFlowline = geom_to_geojson()
    feature2 = geojson.Feature(geometry=nhdFlowline, id='nhdFlowline')
    ############# Get upstream basins ####################
    for id in catchmentIDs:
        totalBasinGeoms.append(get_total_basin(id))
        # m = MultiPolygon(totalBasinGeoms)
        # m = m.buffer(0)
        # totalBasinGeom = unary_union(m)
    x = 0
    polygons = []
    while x < len(totalBasinGeoms):
        polygons.append(totalBasinGeoms[x][0])
        x +=1
    
    m = MultiPolygon(polygons)

    catchment = geom_to_geojson(m)
    feature3 = geojson.Feature(geometry=catchment, id='upstreamBasin')


    featurecollection = geojson.FeatureCollection([feature1, feature2, feature3])
    # print(featurecollection)
    return featurecollection