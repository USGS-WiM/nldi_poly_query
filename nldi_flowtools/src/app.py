
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from .nldi_flowtools import flowtrace, splitcatchment, poly_Query
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

    # lat = float(request.args.get('lat'))
    # lng = float(request.args.get('lng'))
    lnglat = request.args.get('lnglat')
    # print('lnglat:', lnglat)
    polygon_query = bool(util.strtobool(request.args.get('query_polygon')))
    # runsplitcatchment = request.args.get('runsplitcatchment')
    # truefalse = bool(util.strtobool(request.args.get('truefalse')))
    # direction = request.args.get('direction')
    # print("lat:", lat, 'lng:', lng, 'runsplitcatchment:', runsplitcatchment, 'trueflase:', truefalse, 'direction:', direction)

    # if polygon_query == False:
    # ############# Splitcatchment ##############
    #     if runsplitcatchment == 'true':
    #         results = splitcatchment(lng, lat, truefalse)
    #         print('splitcatchment results:', results)

    # ############### Flowtrace ###############
    #     if runsplitcatchment == 'false':
    #         results = flowtrace(lng, lat, truefalse, direction)
    #         print('flowtrace results:', results)

    ############### Polygon Query ############# 
    if polygon_query == True:
        lnglat = lnglat.split(',')
        p_list = []
        for num in lnglat:
            p_list.append(float(num))
        print('unstrung lnglat', p_list)
        results = poly_Query(p_list)
        # print('polygon results:', results)

    # print("results: ", type(results) , results)
    return results