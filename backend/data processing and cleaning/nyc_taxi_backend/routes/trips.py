from flask import Blueprint, jsonify, request
import pandas as pd
from database import engine

trips_bp = Blueprint('trips', __name__)

@trips_bp.route('/trips', methods=['GET'])
def get_trips():
    start = request.args.get('start_datetime')
    end = request.args.get('end_datetime')
    min_dist = request.args.get('min_distance', type=float, default=0)
    max_dist = request.args.get('max_distance', type=float, default=1000)

    query = "SELECT * FROM taxi_trips WHERE trip_distance BETWEEN :min_dist AND :max_dist"
    params = {"min_dist": min_dist, "max_dist": max_dist}

    if start:
        query += " AND pickup_datetime >= :start"
        params["start"] = start
    if end:
        query += " AND pickup_datetime <= :end"
        params["end"] = end

    df = pd.read_sql(query, engine, params=params)
    return jsonify(df.to_dict(orient='records'))