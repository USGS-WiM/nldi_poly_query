from .utils import geom_to_geojson, get_local_catchments, get_local_flowlines
from geojson import Feature, FeatureCollection
from shapely.geometry import MultiPolygon

class Poly_Query:

    def __init__(self, coords=list, get_flowlines=bool, downstream_dist=int):
        self.coords = coords
        self.get_flowlines = get_flowlines
        self.downstream_dist = downstream_dist
        self.catchmentIDs = None 
        self.catchmentGeom = None
        self.totalBasinGeoms = []
        self.upcatchmentGeom = None
        self.flowlinesGeom = None
        self.flowlines = None
        self.downstreamflowlines = None

        self.run()

    def serialize(self):   
        catchments = geom_to_geojson(self.catchmentGeom)
        feature1 = Feature(geometry=catchments, id='catchment', properties={'catchmentID': self.catchmentIDs})

        if self.get_flowlines is True:
            flowlines = geom_to_geojson(self.flowlinesGeom)
            feature3 = Feature(geometry=flowlines, id='flowlinesGeom')
            featurecollection = FeatureCollection([feature1, feature3])

        if self.get_flowlines is False:
            featurecollection = FeatureCollection([feature1])
            
        return featurecollection

    def run(self):
        print('Running poly_query.py')

        #################### Get the catchments that are overlapped by the polygon ########################       
        # If there is only one polygon to query
        if not type(self.coords[0][0]) is list:
            print('Single polygon query')
            self.catchmentIDs, self.catchmentGeom = get_local_catchments(self.coords) 
        
        # If there is more than one polygon to query
        if type(self.coords[0][0]) is list:
            print('Multiple polygons query')
            self.catchmentIDs = []
            self.catchmentGeom = []
            for x in self.coords:
                if type(x[0][0][0]) is list:
                    for y in x:
                        print('multi polygon')
                        self.catchmentIDs.extend(get_local_catchments(y[0])[0])
                        self.catchmentGeom.extend(get_local_catchments(y[0])[1])
                else:
                    print('one of the multiple polygons')
                    self.catchmentIDs.extend(get_local_catchments(x[0])[0])
                    self.catchmentGeom.extend(get_local_catchments(x[0])[1])
            # print('self.catchmentGeom:', self.catchmentGeom)
            
            x = 0
            polygons = []
            while x < len( self.catchmentGeom):
                polygons.append( self.catchmentGeom[x])
                x +=1
            self.catchmentGeom = MultiPolygon(polygons)

        ############################################# Get only flowlines ######################################
        if self.get_flowlines is True:
            print('Getting flowlines')
            # Get all flowlines
            self.flowlines, self.downstreamflowlines, self.flowlinesGeom = get_local_flowlines(self.catchmentIDs, self.downstream_dist)
            
        ####################################### Get no features ##################################################
        if self.get_flowlines is False:
            pass 