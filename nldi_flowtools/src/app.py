
from flask import Flask, request
from flask_cors import CORS, cross_origin
from .nldi_flowtools import flowtrace, splitcatchment
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

    
############# Splitcatchment ##############
    if runsplitcatchment == 'true':
        results = splitcatchment(lng, lat, truefalse)

############### Flowtrace ###############
    if runsplitcatchment == 'false':
        results = flowtrace(lng, lat, truefalse, direction)

    # print("results: ", type(results) , results)
    return results