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
            # print(featurecollection)
            return featurecollection

        # if self.get_flowlines is True:
        #     flowlines = geom_to_geojson(self.nhdflowlines)
        #     feature3 = geojson.Feature(geometry=flowlines, id='nhdFlowlines')
            


    def run(self):
        # Get the catchments that are overlapped by the polygon
        self.catchmentIDs, self.catchmentGeom = get_local_catchments(self.poly)  

        if self.get_upstream is True:
            # Get all upstream catchments
            for id in self.catchmentIDs:
                self.totalBasinGeoms.append(get_total_basin(id))
                # m = MultiPolygon(totalBasinGeoms)
                # m = m.buffer(0)
                # totalBasinGeom = unary_union(m)
            x = 0
            polygons = []
            while x < len( self.totalBasinGeoms):
                polygons.append( self.totalBasinGeoms[x][0])
                x +=1
            self.upcatchmentGeom = MultiPolygon(polygons)

        if self.get_flowlines is True:
            # for id in self.catchmentIDs:
            self.flowlines, self.nhdflowlines = get_local_flowlines(self.catchmentIDs)
