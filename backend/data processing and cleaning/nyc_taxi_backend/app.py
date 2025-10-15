from flask import Blueprint, jsonify, request
import pandas as pd
from sklearn.cluster import DBSCAN
from database import engine

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/hotspots', methods=['GET'])
def get_hotspots():
    eps = float(request.args.get('eps', 0.01))
    min_samples = int(request.args.get('min_samples', 50))
    
    df = pd.read_sql("SELECT pickup_latitude, pickup_longitude FROM taxi_trips", engine)
    coords = df[['pickup_latitude', 'pickup_longitude']].to_numpy()
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    df['cluster'] = clustering.labels_
    
    clusters_summary = df.groupby('cluster').agg({
        'pickup_latitude': 'mean',
        'pickup_longitude': 'mean',
        'cluster': 'count'
    }).rename(columns={'cluster': 'num_trips'}).reset_index()
    
    return jsonify(clusters_summary.to_dict(orient='records'))

@analysis_bp.route('/peak_traffic', methods=['GET'])
def peak_traffic():
    agg_type = request.args.get('type', 'hour')
    df = pd.read_sql("SELECT pickup_datetime FROM taxi_trips", engine)
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    
    if agg_type == 'hour':
        df['hour'] = df['pickup_datetime'].dt.hour
        counts = df.groupby('hour').size().reset_index(name='num_trips')
    else:
        df['weekday'] = df['pickup_datetime'].dt.day_name()
        counts = df.groupby('weekday').size().reset_index(name='num_trips')
    
    return jsonify(counts.to_dict(orient='records'))

@analysis_bp.route('/trip_density', methods=['GET'])
def trip_density():
    start = request.args.get('start_datetime')
    end = request.args.get('end_datetime')
    
    query = "SELECT * FROM taxi_trips WHERE 1=1"
    params = {}
    if start:
        query += " AND pickup_datetime >= :start"
        params["start"] = start
    if end:
        query += " AND pickup_datetime <= :end"
        params["end"] = end
    
    df = pd.read_sql(query, engine, params=params)
    counts = df.groupby(['pickup_latitude', 'pickup_longitude']).size().reset_index(name='num_trips')
    
    return jsonify(counts.to_dict(orient='records'))