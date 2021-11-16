from utils import geom_to_geojson, get_local_catchment, get_local_flowline, get_coordsys, \
    project_point, get_flowgrid, get_onFlowline, get_raindropPath, get_intersectionPoint, get_reachMeasure, \
    split_flowline
from geojson import Feature, FeatureCollection


class Flowtrace:

    """Define inputs and outputs for the main Flowtrace class"""

    def __init__(self, x=None, y=None, raindropTrace=bool, direction=str):

        self.x = x
        self.y = y
        self.raindropTrace = raindropTrace
        self.direction = direction
        self.catchmentIdentifier = None
        self.flowline = None
        self.flw = None
        self.flwdir_transform = None
        self.projected_xy = None
        self.onFlowline = bool

        # geoms
        self.catchmentGeom = None
        self.splitCatchmentGeom = None
        self.upstreamBasinGeom = None
        self.mergedCatchmentGeom = None
        self.intersectionPointGeom = None
        self.raindropPathGeom = None
        self.nhdFlowlineGeom = None
        self.upstreamFlowlineGeom = None
        self.downstreamFlowlineGeom = None
        self.downstreamPathGeom = None

        # outputs
        self.catchment = None
        self.splitCatchment = None
        self.upstreamBasin = None
        self.mergedCatchment = None
        self.intersectionPoint = None
        self.raindropPath = None
        self.nhdFlowline = None
        self.streamInfo = None
        self.upstreamFlowline = None
        self.downstreamFlowline = None
        self.downstreamPath = None

        # create transform
        self.transformToRaster = None
        self.transformToWGS84 = None

        # kick off
        self.run()

    def serialize(self):
        print('Flowtrace variables, self.raindropTrace:', self.raindropTrace)

        if self.onFlowline is True:
            if self.direction == 'up':
                feature1 = Feature(geometry=self.upstreamFlowline, id='upstreamFlowline', properties=self.streamInfo)
                featurecollection = FeatureCollection([feature1])

            if self.direction == 'down':
                feature1 = Feature(geometry=self.downstreamFlowline, id='downstreamFlowline', properties=self.streamInfo)
                featurecollection = FeatureCollection([feature1])

            if self.direction == 'none':
                feature1 = Feature(geometry=self.nhdFlowline, id='nhdFlowline', properties=self.streamInfo)
                featurecollection = FeatureCollection([feature1])

        if self.onFlowline is False:
            if self.direction == 'up' and self.raindropTrace is True:
                feature1 = Feature(geometry=self.upstreamFlowline, id='upstreamFlowline', properties=self.streamInfo)
                feature2 = Feature(geometry=self.raindropPath, id='raindropPath')
                featurecollection = FeatureCollection([feature1, feature2])

            if self.direction == 'down' and self.raindropTrace is True:
                feature1 = Feature(geometry=self.downstreamFlowline, id='downstreamFlowline', properties=self.streamInfo)
                feature2 = Feature(geometry=self.raindropPath, id='raindropPath')
                featurecollection = FeatureCollection([feature1, feature2])
                # feature1 = Feature(geometry=self.downstreamPath, id='downstreamPath', properties=self.streamInfo)
                # featurecollection = FeatureCollection([feature1])

            if self.direction == 'none' and self.raindropTrace is True:
                feature1 = Feature(geometry=self.nhdFlowline, id='nhdFlowline', properties=self.streamInfo)
                feature2 = Feature(geometry=self.raindropPath, id='raindropPath')
                featurecollection = FeatureCollection([feature1, feature2])

            if self.direction == 'up' and self.raindropTrace is False:
                feature1 = Feature(geometry=self.upstreamFlowline, id='upstreamFlowline', properties=self.streamInfo)
                featurecollection = FeatureCollection([feature1])

            if self.direction == 'down' and self.raindropTrace is False:
                feature1 = Feature(geometry=self.downstreamFlowline, id='downstreamFlowline', properties=self.streamInfo)
                featurecollection = FeatureCollection([feature1])

            if self.direction == 'none' and self.raindropTrace is False:
                feature1 = Feature(geometry=self.nhdFlowline, id='nhdFlowline', properties=self.streamInfo)
                featurecollection = FeatureCollection([feature1])

        # print('featurecollection', type(featurecollection))
        return featurecollection

# main functions
    def run(self):
        # Order of these functions is important!
        self.catchmentIdentifier, self.catchmentGeom = get_local_catchment(self.x, self.y)
        self.flowline, self.nhdFlowlineGeom = get_local_flowline(self.catchmentIdentifier)
        self.transformToRaster, self.transformToWGS84 = get_coordsys()
        self.projected_xy = project_point(self.x, self.y, self.transformToRaster)
        self.flw, self.flwdir_transform = get_flowgrid(self.catchmentGeom, self.transformToRaster)
        self.onFlowline = get_onFlowline(self.projected_xy, self.flowline, self.transformToRaster)
        self.catchment = geom_to_geojson(self.catchmentGeom)

        if self.onFlowline is True:
            self.intersectionPointGeom = get_intersectionPoint(self.x, self.y, self.onFlowline)
            self.streamInfo = get_reachMeasure(self.intersectionPointGeom, self.flowline)
            self.upstreamFlowlineGeom, self.downstreamFlowlineGeom = split_flowline(self.intersectionPointGeom, self.flowline)

            # Outputs
            if self.direction == 'up':
                self.upstreamFlowline = geom_to_geojson(self.upstreamFlowlineGeom)

            if self.direction == 'down':
                self.downstreamFlowline = geom_to_geojson(self.downstreamFlowlineGeom)

            if self.direction == 'none':
                self.nhdFlowline = geom_to_geojson(self.nhdFlowlineGeom)

        if self.onFlowline is False:
            self.raindropPathGeom = get_raindropPath(self.flw, self.projected_xy,  self.nhdFlowlineGeom, self.flowline, self.transformToRaster, self.transformToWGS84)
            self.intersectionPointGeom = get_intersectionPoint(self.x, self.y, self.onFlowline, self.raindropPathGeom)
            # self.streamInfo = get_reachMeasure(self.intersectionPointGeom, self.flowline)
            self.upstreamFlowlineGeom, self.downstreamFlowlineGeom = split_flowline(self.intersectionPointGeom, self.flowline)

            # Outputs
            if self.direction == 'up' and self.raindropTrace is True:
                self.upstreamFlowline = geom_to_geojson(self.upstreamFlowlineGeom)
                self.raindropPath = geom_to_geojson(self.raindropPathGeom)

            if self.direction == 'down' and self.raindropTrace is True:
                self.downstreamFlowline = geom_to_geojson(self.downstreamFlowlineGeom)
                self.raindropPath = geom_to_geojson(self.raindropPathGeom)
                # self.downstreamPathGeom = merge_downstreamPath(self.raindropPathGeom, self.downstreamFlowlineGeom)
                # self.downstreamPath = geom_to_geojson(self.downstreamPathGeom)

            if self.direction == 'none' and self.raindropTrace is True:
                self.nhdFlowline = geom_to_geojson(self.nhdFlowlineGeom)
                self.raindropPath = geom_to_geojson(self.raindropPathGeom)

            if self.direction == 'up' and self.raindropTrace is False:
                self.upstreamFlowline = geom_to_geojson(self.upstreamFlowlineGeom)

            if self.direction == 'down' and self.raindropTrace is False:
                self.downstreamFlowline = geom_to_geojson(self.downstreamFlowlineGeom)

            if self.direction == 'none' and self.raindropTrace is False:
                self.nhdFlowline = geom_to_geojson(self.nhdFlowlineGeom)

            if self.raindropTrace is True:
                self.streamInfo = get_reachMeasure(self.intersectionPointGeom, self.flowline, self.raindropPathGeom)
            if self.raindropTrace is False:
                self.streamInfo = get_reachMeasure(self.intersectionPointGeom, self.flowline)

        # self.intersectionPoint = geom_to_geojson(self.intersectionPointGeom)
# print('featurecollection', type(featurecollection))
# return featurecollection
