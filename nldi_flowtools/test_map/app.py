
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from src.nldi_flowtools import flowtrace, splitcatchment
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

    lat = float(request.args.get('lat'))
    lng = float(request.args.get('lng'))
    runsplitcatchment = request.args.get('runsplitcatchment')
    truefalse = bool(util.strtobool(request.args.get('truefalse')))
    direction = request.args.get('direction')
    print("lat:", lat, 'lng:', lng, 'runsplitcatchment:', runsplitcatchment, 'trueflase:', truefalse, 'direction:', direction)

    
############# Splitcatchment ##############
    if runsplitcatchment == 'true':
        results = splitcatchment(lng, lat, truefalse)
        print('splitcatchment results:', results)

############### Flowtrace ###############
    if runsplitcatchment == 'false':
        results = flowtrace(lng, lat, truefalse, direction)
        print('flowtrace results:', results)

    # print("results: ", type(results) , results)
    return results