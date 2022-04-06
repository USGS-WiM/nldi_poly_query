from flask import Flask, request
from flask_cors import CORS, cross_origin
from .nldi_flowtools import poly_query
from distutils import util
import time
import json

app = Flask(__name__)
cors = CORS(app, origin=["http://127.0.0.1:5000"])
app.config['CORS_HEADERS'] = 'Content-Type'

# @app.route("/")

def home():
    return "sample server"

@app.route("/flowtools")
@cross_origin(origin='*')
def main():

    tic = time.perf_counter()
    polygon_query = bool(util.strtobool(request.args.get('query_polygon')))

    if polygon_query == False:
        print('false')

    ############### Polygon Query ############# 
    if polygon_query == True:
        print('Running app.py')
        getFlowlines =  bool(util.strtobool(request.args.get('getFlowlines')))
        lnglat = request.args.get('lnglat')
        lnglat = json.loads(lnglat)
        downstream_dist = request.args.get('downstream_dist')
        results = poly_query(lnglat, getFlowlines, downstream_dist)

    # print("results: ", type(results) , results)

    toc = time.perf_counter()
    print(f"Flowtools completed in {toc - tic:0.4f} seconds")
    return results