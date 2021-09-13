from .utils import geom_to_geojson, get_local_catchment, get_local_flowlines, get_coordsys, \
    project_point, get_total_basin, split_catchment, get_onFlowline, get_upstream_basin, merge_geometry
import geojson
from shapely.ops import unary_union
from shapely.geometry import MultiPolygon

class Poly_Splitcatchment:

    def __init__(self, poly=list, get_upstream=bool, get_flowlines=bool):
        self.poly = poly
        self.get_upstream = get_upstream
        self.get_flowlines = get_flowlines
        self.catchmentIDs = None 
        self.catchmentGeom = None
        self.totalBasinGeoms = []
        self.upcatchmentGeom = None

        self.run()

    def serialize(self):

        catchments = geom_to_geojson(self.catchmentGeom)
        feature1 = geojson.Feature(geometry=catchments, id='catchment', properties={'catchmentID': self.catchmentIDs})

        if self.get_upstream is True:
            upcatchment = geom_to_geojson(self.upcatchmentGeom)
            feature3 = geojson.Feature(geometry=upcatchment, id='upstreamBasin')

            featurecollection = geojson.FeatureCollection([feature1,  feature3])
            # print(featurecollection)
            return featurecollection

        if self.get_flowlines is True:
            pass


    def run(self):
        # Get the catchments that are overlapped by the polygon
        self.catchmentIDs, self.catchmentGeom = get_local_catchment(self.poly)  

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
            for id in self.catchmentIDs:
