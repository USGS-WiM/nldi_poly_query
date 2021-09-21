from .utils import geom_to_geojson, get_local_catchment, get_local_flowline, get_coordsys, \
    project_point, get_total_basin, split_catchment, get_onFlowline, get_upstream_basin, merge_geometry
import geojson


class SplitCatchment:

    """Define inputs and outputs for the main SplitCatchment class"""

    def __init__(self, x=None, y=None, upstream=bool):

        self.x = x
        self.y = y
        self.catchmentIdentifier = None
        self.flowline = None
        self.flw = None
        self.flwdir_transform = None
        self.projected_xy = None
        self.onFlowline = bool
        self.upstream = upstream

        # geoms
        self.catchmentGeom = None
        self.splitCatchmentGeom = None
        self.totalBasinGeom = None
        self.upstreamBasinGeom = None
        self.mergedCatchmentGeom = None
        self.nhdFlowlineGeom = None

        # outputs
        self.catchment = None
        self.splitCatchment = None
        self.upstreamBasin = None
        self.mergedCatchment = None

        # create transform
        self.transformToRaster = None
        self.transformToWGS84 = None

        # kick off
        self.run()

    def serialize(self):

        print('Splitcatment variable, self.upstream: ', self.upstream)
        # If upstream == False, only return the local catchment and the splitcatchment geometries
        if self.upstream is False:
            feature1 = geojson.Feature(geometry=self.catchment, id='catchment', properties={'catchmentID': self.catchmentIdentifier})
            feature2 = geojson.Feature(geometry=self.splitCatchment, id='splitCatchment')
            featurecollection = geojson.FeatureCollection([feature1, feature2])

        # If upstream == True and the clickpoint is on a NHD FLowline, return the local catchment and the merged catchment (splitcatchment merged with all upstream basins)
        if self.upstream is True and self.onFlowline is True:
            feature1 = geojson.Feature(geometry=self.catchment, id='catchment', properties={'catchmentID': self.catchmentIdentifier})
            feature2 = geojson.Feature(geometry=self.mergedCatchment, id='mergedCatchment')
            featurecollection = geojson.FeatureCollection([feature1, feature2])

        # If upstream == True and the clickpoint is NOT on a NHD FLowline, return the local catchment and splitcatchment 
        if self.upstream is True and self.onFlowline is False:
            feature1 = geojson.Feature(geometry=self.catchment, id='catchment', properties={'catchmentID': self.catchmentIdentifier})
            feature2 = geojson.Feature(geometry=self.splitCatchment, id='splitCatchment')
            # feature3 = geojson.Feature(geometry=self.upstreamBasin, id='upstreamBasin')
            featurecollection = geojson.FeatureCollection([feature1, feature2])

        # print(featurecollection)
        return featurecollection

# main functions
    def run(self):
        # Order of these functions is important!
        self.catchmentIdentifier, self.catchmentGeom = get_local_catchment(self.x, self.y)
        self.flowline, self.nhdFlowlineGeom = get_local_flowline(self.catchmentIdentifier)
        self.transformToRaster, self.transformToWGS84 = get_coordsys()
        self.projected_xy = project_point(self.x, self.y, self.transformToRaster)
        self.splitCatchmentGeom = split_catchment(self.catchmentGeom, self.projected_xy, self.transformToRaster, self.transformToWGS84)
        self.onFlowline = get_onFlowline(self.projected_xy, self.flowline, self.transformToRaster)
        self.catchment = geom_to_geojson(self.catchmentGeom)

        # outputs
        if self.upstream is False:
            self.splitCatchment = geom_to_geojson(self.splitCatchmentGeom)

        if self.upstream is True and self.onFlowline is True:
            self.totalBasinGeom = get_total_basin(self.catchmentIdentifier)
            self.mergedCatchmentGeom = merge_geometry(self.catchmentGeom, self.splitCatchmentGeom, self.totalBasinGeom)
            self.mergedCatchment = geom_to_geojson(self.mergedCatchmentGeom)

        if self.upstream is True and self.onFlowline is False:
            self.splitCatchment = geom_to_geojson(self.splitCatchmentGeom)
            # self.totalBasinGeom = get_total_basin(self.catchmentIdentifier)
            # self.upstreamBasinGeom = get_upstream_basin(self.catchmentGeom, self.totalBasinGeom)
            # self.upstreamBasin = geom_to_geojson(self.upstreamBasinGeom)
