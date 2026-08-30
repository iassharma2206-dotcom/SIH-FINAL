"""
live_traffic.py
Real-time TomTom Flow Segment Data for the QPSO optimizer.
Separate from api.py's get_road_path (which is display-only).
This is the ONLY file that should call TomTom for optimization purposes.
"""

import os
import time as time_module
import requests

_cache = {}          # {(round(lat,3), round(lon,3)): (timestamp, ratio)}
_CACHE_TTL = 180      # seconds
_call_log = []        # audit trail: list of dicts, see get_call_log()
_MAX_CALLS_PER_MIN = 40
_call_timestamps = []


def _get_key():
    """
    Reads TOMTOM_API_KEY the same way the rest of the app already does.
    Checks os.environ first (covers .env via python-dotenv if already
    loaded elsewhere in the app), then tries config.py as a second source.
    Never raises — returns None if not found anywhere.
    """
    key = os.environ.get('TOMTOM_API_KEY')
    if key and key != 'your_tomtom_api_key_here':
        return key
    try:
        from config import TOMTOM_API_KEY as CONFIG_KEY
        if CONFIG_KEY and CONFIG_KEY != 'your_tomtom_api_key_here':
            return CONFIG_KEY
    except Exception:
        pass
    # Also check .env file if accessible
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line_s = line.strip()
                    if line_s.startswith("TOMTOM_API_KEY"):
                        parts = line_s.split("=", 1)
                        if len(parts) == 2:
                            candidate = parts[1].strip().strip('"').strip("'")
                            if candidate and candidate != "your_tomtom_api_key_here":
                                return candidate
    except Exception:
        pass
    return None


def _rate_limit_ok():
    """Returns True if under 40 calls/min, prunes old timestamps."""
    now = time_module.time()
    global _call_timestamps
    _call_timestamps = [t for t in _call_timestamps if now - t < 60]
    return len(_call_timestamps) < _MAX_CALLS_PER_MIN


def get_live_ratio(lat, lon):
    """
    Returns (ratio, source) where:
      ratio: float, currentSpeed/freeFlowSpeed, clamped [0.15, 1.0].
             Returns None if live data genuinely unavailable.
      source: 'live_api' | 'cache' | 'unavailable'

    NEVER raises. Logs every call to _call_log for audit purposes.
    """
    key = (round(lat, 3), round(lon, 3))
    now = time_module.time()

    if key in _cache:
        ts, ratio = _cache[key]
        if now - ts < _CACHE_TTL:
            _call_log.append({'ts': now, 'lat': lat, 'lon': lon,
                               'source': 'cache', 'ratio': ratio})
            return ratio, 'cache'

    api_key = _get_key()
    if not api_key or not _rate_limit_ok():
        _call_log.append({'ts': now, 'lat': lat, 'lon': lon,
                           'source': 'unavailable', 'ratio': None})
        return None, 'unavailable'

    try:
        url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        resp = requests.get(url, params={'point': f'{lat},{lon}', 'key': api_key}, timeout=3)
        _call_timestamps.append(now)
        if resp.status_code != 200:
            _call_log.append({'ts': now, 'lat': lat, 'lon': lon,
                               'source': 'unavailable', 'ratio': None,
                               'http_status': resp.status_code})
            return None, 'unavailable'

        data = resp.json().get('flowSegmentData', {})
        current = data.get('currentSpeed')
        free_flow = data.get('freeFlowSpeed')

        if not current or not free_flow or free_flow == 0:
            _call_log.append({'ts': now, 'lat': lat, 'lon': lon,
                               'source': 'unavailable', 'ratio': None})
            return None, 'unavailable'

        ratio = max(0.15, min(1.0, current / free_flow))
        _cache[key] = (now, ratio)
        _call_log.append({'ts': now, 'lat': lat, 'lon': lon,
                           'source': 'live_api', 'ratio': ratio,
                           'current_speed': current, 'free_flow_speed': free_flow})
        return ratio, 'live_api'

    except Exception as e:
        _call_log.append({'ts': now, 'lat': lat, 'lon': lon,
                           'source': 'unavailable', 'ratio': None,
                           'error': str(e)})
        return None, 'unavailable'


def get_call_log():
    """Returns a copy of _call_log, for audit/verification."""
    return list(_call_log)


def get_call_summary():
    """
    Returns dict: {'total': int, 'live_api': int, 'cache': int,
    'unavailable': int, 'live_pct': float}
    """
    total = len(_call_log)
    live = sum(1 for c in _call_log if c['source'] == 'live_api')
    cache = sum(1 for c in _call_log if c['source'] == 'cache')
    unavail = sum(1 for c in _call_log if c['source'] == 'unavailable')
    return {
        'total': total, 'live_api': live, 'cache': cache,
        'unavailable': unavail,
        'live_pct': round(100 * live / total, 1) if total else 0.0
    }
