from .utils import geom_to_geojson, get_local_catchments, get_local_flowlines, get_total_basin
import geojson
from shapely.geometry import MultiPolygon

class Poly_Query:

    def __init__(self, poly=list, get_upstream=bool, get_flowlines=bool):
        self.poly = poly
        self.get_upstream = get_upstream
        self.get_flowlines = get_flowlines
        self.catchmentIDs = None 
        self.catchmentGeom = None
        self.totalBasinGeoms = []
        self.upcatchmentGeom = None
        self.nhdflowlines = None
        self.flowlines = None

        self.run()

    def serialize(self):

        catchments = geom_to_geojson(self.catchmentGeom)
        feature1 = geojson.Feature(geometry=catchments, id='catchment', properties={'catchmentID': self.catchmentIDs})

        if self.get_upstream is True and self.get_flowlines is True:
            upcatchment = geom_to_geojson(self.upcatchmentGeom)
            feature2 = geojson.Feature(geometry=upcatchment, id='upstreamBasin')

            flowlines = geom_to_geojson(self.nhdflowlines)
            feature3 = geojson.Feature(geometry=flowlines, id='nhdFlowlines')

            featurecollection = geojson.FeatureCollection([feature1, feature2, feature3])
            
            return featurecollection

        if self.get_upstream is False and self.get_flowlines is True:

            flowlines = geom_to_geojson(self.nhdflowlines)
            feature3 = geojson.Feature(geometry=flowlines, id='nhdFlowlines')

            featurecollection = geojson.FeatureCollection([feature1, feature3])
            
            return featurecollection

        if self.get_upstream is True and self.get_flowlines is False:
            upcatchment = geom_to_geojson(self.upcatchmentGeom)
            feature2 = geojson.Feature(geometry=upcatchment, id='upstreamBasin')

            featurecollection = geojson.FeatureCollection([feature1, feature2])
            
            return featurecollection

        if self.get_upstream is False and self.get_flowlines is False:
            featurecollection = geojson.FeatureCollection([feature1])
            
            return featurecollection

    def run(self):
        # Get the catchments that are overlapped by the polygon
        print('Running poly_query.py')
        self.catchmentIDs, self.catchmentGeom = get_local_catchments(self.poly) 

        print('Variables:', type(self.get_upstream), self.get_flowlines)

        if self.get_upstream is True and self.get_flowlines is True:
            # Get all upstream catchments
            for id in self.catchmentIDs:
                self.totalBasinGeoms.append(get_total_basin(id))
            x = 0
            polygons = []
            while x < len( self.totalBasinGeoms):
                polygons.append( self.totalBasinGeoms[x][0])
                x +=1
            self.upcatchmentGeom = MultiPolygon(polygons)

            # Get all flowlines
            self.flowlines, self.nhdflowlines = get_local_flowlines(self.catchmentIDs, 75)

        if self.get_upstream is False and self.get_flowlines is True:
            print('Getting flowlines, no upstream basins')
            # Get all flowlines
            self.flowlines, self.nhdflowlines = get_local_flowlines(self.catchmentIDs, 75)

        if self.get_upstream is True and self.get_flowlines is False:
            # Get all upstream catchments
            for id in self.catchmentIDs:
                self.totalBasinGeoms.append(get_total_basin(id))
            x = 0
            polygons = []
            while x < len( self.totalBasinGeoms):
                polygons.append( self.totalBasinGeoms[x][0])
                x +=1
            self.upcatchmentGeom = MultiPolygon(polygons)

        if self.get_upstream is False and self.get_flowlines is False:
            pass 