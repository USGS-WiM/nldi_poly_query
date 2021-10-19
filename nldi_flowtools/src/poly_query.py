from .utils import geom_to_geojson, get_local_catchments, get_local_flowlines, get_total_basin
from geojson import Feature, FeatureCollection
from shapely.geometry import MultiPolygon

class Poly_Query:

    def __init__(self, coords=list, get_upstream=bool, get_flowlines=bool, downstream_dist=int, returnGeoms=bool):
        self.coords = coords
        self.get_upstream = get_upstream
        self.get_flowlines = get_flowlines
        self.downstream_dist = downstream_dist
        self.returnGeoms = returnGeoms
        self.catchmentIDs = None 
        self.catchmentGeom = None
        self.totalBasinGeoms = []
        self.upcatchmentGeom = None
        self.flowlinesGeom = None
        self.flowlines = None
        self.downstreamflowlines = None

        self.run()

    def serialize(self):
        if self.returnGeoms:    
            catchments = geom_to_geojson(self.catchmentGeom)
            feature1 = Feature(geometry=catchments, id='catchment', properties={'catchmentID': self.catchmentIDs})

            if self.get_upstream is True and self.get_flowlines is True:
                upcatchment = geom_to_geojson(self.upcatchmentGeom)
                feature2 = Feature(geometry=upcatchment, id='upstreamBasin')

                flowlines = geom_to_geojson(self.flowlinesGeom)
                feature3 = Feature(geometry=flowlines, id='flowlinesGeom')

                featurecollection = FeatureCollection([feature1, feature2, feature3])
                
                return featurecollection

            if self.get_upstream is False and self.get_flowlines is True:

                flowlines = geom_to_geojson(self.flowlinesGeom)
                feature3 = Feature(geometry=flowlines, id='flowlinesGeom')

                featurecollection = FeatureCollection([feature1, feature3])
                
                return featurecollection

            if self.get_upstream is True and self.get_flowlines is False:
                upcatchment = geom_to_geojson(self.upcatchmentGeom)
                feature2 = Feature(geometry=upcatchment, id='upstreamBasin')

                featurecollection = FeatureCollection([feature1, feature2])
                
                return featurecollection

            if self.get_upstream is False and self.get_flowlines is False:
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
            if self.returnGeoms:
                x = 0
                polygons = []
                while x < len( self.catchmentGeom):
                    polygons.append( self.catchmentGeom[x])
                    x +=1
                self.catchmentGeom = MultiPolygon(polygons)

        print('Variables:', type(self.get_upstream), self.get_flowlines)

        ####################### Get both upstream basins and flowlines ######################################
        if self.get_upstream is True and self.get_flowlines is True:
            # Get all upstream catchments
            print('self.catchmentIDs:', self.catchmentIDs)
            for id in self.catchmentIDs:
                self.totalBasinGeoms.append(get_total_basin(id))
            x = 0
            polygons = []
            while x < len( self.totalBasinGeoms):
                polygons.append( self.totalBasinGeoms[x][0])
                x +=1
            self.upcatchmentGeom = MultiPolygon(polygons)

            # Get all flowlines
            self.flowlines, self.downstreamflowlines, self.flowlinesGeom = get_local_flowlines(self.catchmentIDs, self.returnGeoms, self.downstream_dist)

        ############################################# Get only flowlines ######################################
        if self.get_upstream is False and self.get_flowlines is True:
            print('Getting flowlines, no upstream basins')
            # Get all flowlines
            self.flowlines, self.downstreamflowlines, self.flowlinesGeom = get_local_flowlines(self.catchmentIDs, self.returnGeoms, self.downstream_dist)
            
        ########################################### Get only upstream basins #####################################
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

        ####################################### Get no features ##################################################
        if self.get_upstream is False and self.get_flowlines is False:
            pass 