"""
backend/maps/traffic_adjustment.py
Applies real TomTom Flow Segment data (via root live_traffic.py) to the
backend's own distance/time matrix, with graceful fallback to
backend/maps/traffic_model.py's existing synthetic schedule if live data
is unavailable for a given edge.
"""
import sys
import os
import numpy as np

# Ensure root directory is accessible for live_traffic import if needed
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from live_traffic import get_live_ratio
except Exception:
    def get_live_ratio(lat, lon):
        return None, 'unavailable'

try:
    from backend.maps.traffic_model import get_traffic_multiplier
except Exception:
    def get_traffic_multiplier(highway_type="primary", time_hour=9.0):
        return 1.0


def apply_real_traffic(time_matrix, nodes):
    """
    Args:
        time_matrix: numpy array of travel times in hours
        nodes: list of node dicts/objects with 'coords' (lat, lon)
    Returns:
        new numpy array with traffic adjusted travel times (hours).
    """
    try:
        n = len(nodes)
        adjusted = np.array(time_matrix, dtype=float).copy()
        synth_mult = get_traffic_multiplier()

        for i in range(n):
            for j in range(n):
                if i == j or time_matrix[i, j] == 0:
                    continue
                c1 = nodes[i].get('coords', (0.0, 0.0))
                c2 = nodes[j].get('coords', (0.0, 0.0))
                lat = (float(c1[0]) + float(c2[0])) / 2.0
                lon = (float(c1[1]) + float(c2[1])) / 2.0

                ratio, source = get_live_ratio(lat, lon)
                if ratio is not None and ratio > 0:
                    adjusted[i, j] = time_matrix[i, j] / ratio
                else:
                    adjusted[i, j] = time_matrix[i, j] * synth_mult

        return adjusted
    except Exception:
        return time_matrix
