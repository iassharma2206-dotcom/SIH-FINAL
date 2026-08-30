# Time-of-day synthetic congestion multipliers
TRAFFIC_MULTIPLIERS = {
    "motorway":    {"peak_morning": 1.4, "peak_evening": 1.6, "off_peak": 1.0},
    "trunk":       {"peak_morning": 1.5, "peak_evening": 1.7, "off_peak": 1.0},
    "primary":     {"peak_morning": 1.6, "peak_evening": 1.8, "off_peak": 1.0},
    "secondary":   {"peak_morning": 1.3, "peak_evening": 1.4, "off_peak": 1.0},
    "residential": {"peak_morning": 1.2, "peak_evening": 1.2, "off_peak": 1.0}
}

def get_traffic_multiplier(highway_type="primary", time_hour=9.0):
    """
    Returns time-of-day traffic multiplier for edge travel times.
    Peak morning: 8:00 - 10:00
    Peak evening: 17:00 - 20:00
    """
    if isinstance(highway_type, list):
        highway_type = highway_type[0]
        
    h_type = str(highway_type).lower()
    match_type = "primary"
    for key in TRAFFIC_MULTIPLIERS.keys():
        if key in h_type:
            match_type = key
            break
            
    if 8.0 <= time_hour <= 10.0:
        return TRAFFIC_MULTIPLIERS[match_type]["peak_morning"]
    elif 17.0 <= time_hour <= 20.0:
        return TRAFFIC_MULTIPLIERS[match_type]["peak_evening"]
    else:
        return TRAFFIC_MULTIPLIERS[match_type]["off_peak"]
