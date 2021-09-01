from .utils import geom_to_geojson, get_local_catchment, get_local_flowlines, get_coordsys, \
    project_point, get_total_basin, split_catchment, get_onFlowline, get_upstream_basin, merge_geometry
import geojson

catchmentGeom = None
catchmentIDs = None

def poly_Query(p_list):
    print('running poly_Query')
    print('p_list', p_list)
    catchmentIDs, catchmentGeom = get_local_catchment(p_list)
    print('step 1')
    catchment = geom_to_geojson(catchmentGeom)
    feature1 = geojson.Feature(geometry=catchment, id='catchment', properties={'catchmentID': catchmentIDs})
    featurecollection = geojson.FeatureCollection([feature1])

    # print(featurecollection)
    return featurecollection