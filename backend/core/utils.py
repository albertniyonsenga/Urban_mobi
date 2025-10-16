import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # radius of earth in kilometers
    return c * r

def validate_nyc_coordinates(lat, lon):
    """
    Validate if coordinates are within NYC bounds
    """
    nyc_bounds = {
        'min_lat': 40.5, 'max_lat': 40.9,
        'min_lon': -74.3, 'max_lon': -73.7
    }
    
    return (nyc_bounds['min_lat'] <= lat <= nyc_bounds['max_lat'] and 
            nyc_bounds['min_lon'] <= lon <= nyc_bounds['max_lon'])
