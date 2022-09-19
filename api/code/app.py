import flask
from flask import request, jsonify
from time import perf_counter
import logging as log
from utils.db_utils import run_query
from utils.queries import QUERIES
from datetime import datetime

app = flask.Flask(__name__)
app.config['DEBUG'] = True

log.basicConfig(filename = "/var/log/api.log",
                filemode = "w",
                format='%(asctime)s - %(levelname)s: %(message)s',
                level = log.DEBUG)


@app.route('/', methods=['GET'])
def home():
    return """<h1>Weekly Average Number of Trips per Area</h1>
    <p>Area can be specified by a bounding box coordinates or region/city</p>"""


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/v1/weekly_avg_trips', methods=['GET'])
def weekly_avg_trips():
    """
        The same method can be used to compute average weekly trips in an area by region, bounding box or both (separately).
        
        Query params:
        - date: 
            Date in the format %Y-%m-%d, that belongs to the week we are interesting in computing results.
            Example: 2018-05-28

        - region: 
            String representing a city name. 
            Example: Hamburg

        - box: 
            Valid sequence of comma-separated points enclosed in brackets, representing a closed polygon. 
            The first and last points are expected to be the same.
            Example: (-100 -100,-100 100,100 100,100 -100,-100 -100)
    """
    
    query_params = request.args

    date = query_params.get('date')
    box = query_params.get('box')
    region = query_params.get('region')
    
    if not date:
        return "Required query param missing: 'date'", 400
    if not box and not region:
        return "Required query param missing, at least one of is expected: 'box', 'region'", 400

    try:
        week_year = datetime.strftime(datetime.strptime(date, '%Y-%m-%d'), '%W_%Y')
    except Exception as e:
        return "Please make sure date format is %Y-%m-%d", 400

    start = perf_counter()

    if region:
        results_region, status = run_query(QUERIES['WEEKLY_AVG_BY_REGION'], {'week_year': week_year, 'region': region})
        if not status:
            return "Problem while computing results. Please verify format of API query params", 400
    # TODO: validate box format and ensure it is a valid geometry (closed polygon)
    if box:
        results_box, status = run_query(QUERIES['WEEKLY_AVG_BY_BOX'], {'week_year': week_year, 'box': f'POLYGON({box})'})
        if not status:
            return "Problem while computing results. Please verify format of API query params and ensure box is a closed polygon", 400

    end = perf_counter()
    elapsed_time_ms = round((end - start) * 1000, 3)

    response_region = dict()
    response_box = dict()
    if region:
        response_region = {"avg_trips_area": 0 if not results_region else results_region['weekly_avg'],
                            "total_trips_area": 0 if not results_region else results_region['count_trips'],
                            "region": region,
                            "week_year": week_year,
                            "compute_time_ms": elapsed_time_ms}
    if box:
        response_box = {"avg_trips_area": 0 if not results_box else results_box['weekly_avg'],
                        "total_trips_area": 0 if not results_box else results_box['count_trips'],
                        "box_coords": box,
                        "week_year": week_year,
                        "compute_time_ms": elapsed_time_ms}

    response = {
        "weekly_avg_trips_by_region": response_region,
        "weekly_avg_trips_by_box": response_box,
    }
    return jsonify(response), 200

    

