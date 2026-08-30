"""
traffic_aware.py
Synthetic time-of-day traffic model and hybrid live-or-scheduled traffic adjustment.
"""
from datetime import datetime
import numpy as np


def get_current_hour():
    """Returns current hour of day (0..23)."""
    return datetime.now().hour


def get_traffic_multiplier(hour=None):
    """
    Returns time-of-day traffic multiplier.
    Morning peak (8-10): 1.5x
    Evening peak (17-20): 1.7x
    Off-peak: 1.0x
    """
    if hour is None:
        hour = get_current_hour()
    if 8 <= hour <= 10:
        return 1.5
    elif 17 <= hour <= 20:
        return 1.7
    else:
        return 1.0


def get_traffic_label(hour=None):
    """Returns human-readable congestion label."""
    if hour is None:
        hour = get_current_hour()
    if 8 <= hour <= 10:
        return "Peak Morning"
    elif 17 <= hour <= 20:
        return "Peak Evening"
    else:
        return "Off Peak"


def apply_traffic_to_matrix(time_matrix, hour=None):
    """
    Applies synthetic time-of-day multiplier to time_matrix.
    """
    mult = get_traffic_multiplier(hour)
    return np.array(time_matrix, dtype=float) * mult


def apply_live_or_scheduled_traffic(time_matrix, nodes):
    """
    Preferred traffic adjustment: tries REAL TomTom data per edge first,
    falls back to the existing hour-of-day schedule for any edge where
    live data isn't available (no key, rate limited, API error).

    Args:
        time_matrix: numpy array of travel times in hours
        nodes: list of node dicts with 'coords', same order as time_matrix
               rows/cols (needed to know which lat/lon each edge connects)

    Returns: numpy array, same shape as time_matrix, adjusted times.
    Mixed sourcing is fine and expected — some edges may use live data,
    others the schedule, in the same matrix. This is not a bug.
    """
    from live_traffic import get_live_ratio
    import numpy as np

    n = len(nodes)
    adjusted = np.array(time_matrix, dtype=float).copy()
    schedule_mult = get_traffic_multiplier()  # fallback, computed once

    for i in range(n):
        for j in range(n):
            if i == j or time_matrix[i][j] == 0:
                continue
            lat = (nodes[i]['coords'][0] + nodes[j]['coords'][0]) / 2
            lon = (nodes[i]['coords'][1] + nodes[j]['coords'][1]) / 2
            ratio, source = get_live_ratio(lat, lon)
            if ratio is not None and ratio > 0:
                adjusted[i][j] = time_matrix[i][j] / ratio
            else:
                adjusted[i][j] = time_matrix[i][j] * schedule_mult

    return adjusted
