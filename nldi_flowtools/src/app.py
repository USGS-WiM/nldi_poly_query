
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from .nldi_flowtools import flowtrace, splitcatchment, poly_query
from distutils import util

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")

def home():
    return "sample server"

@app.route("/flowtools")
@cross_origin(origin='*')
def main():


    polygon_query = bool(util.strtobool(request.args.get('query_polygon')))
    

    if polygon_query == False:
        lat = float(request.args.get('lat'))
        lng = float(request.args.get('lng'))        
        runsplitcatchment = request.args.get('runsplitcatchment')
        truefalse = bool(util.strtobool(request.args.get('truefalse')))        
        direction = request.args.get('direction')
        # print("lat:", lat, 'lng:', lng, 'runsplitcatchment:', runsplitcatchment, 'trueflase:', truefalse, 'direction:', direction)

    ############# Splitcatchment ##############
        if runsplitcatchment == 'true':
            results = splitcatchment(lng, lat, truefalse)
            print('splitcatchment results:', results)

    ############### Flowtrace ###############
        if runsplitcatchment == 'false':
            results = flowtrace(lng, lat, truefalse, direction)
            print('flowtrace results:', results)

    ############### Polygon Query ############# 
    if polygon_query == True:
        print('Running app.py')
        getUpstream =  bool(util.strtobool(request.args.get('getUpstream')))
        getFlowlines =  bool(util.strtobool(request.args.get('getFlowlines')))
        lnglat = request.args.get('lnglat')
        lnglat = lnglat.split(',')
        p_list = []
        for num in lnglat:
            p_list.append(float(num))
        print('unstrung lnglat', p_list)
        results = poly_query(p_list, getUpstream, getFlowlines)
        # print('polygon results:', results)

    # print("results: ", type(results) , results)
    return results