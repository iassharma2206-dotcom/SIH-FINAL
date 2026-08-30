import time
import requests
from functools import lru_cache

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "SIH26137-QuantumRouteOptimizer/1.0 (quantum-route@app.local)"
}

# Cache results in memory
_GEOCODE_CACHE = {}
_LAST_REQUEST_TIME = 0.0

def search_location(query: str, limit: int = 5):
    """
    Search places globally via OpenStreetMap Nominatim API with rate limiting and caching.
    """
    global _LAST_REQUEST_TIME
    q = query.strip().lower()
    if not q or len(q) < 2:
        return []
        
    if q in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[q]
        
    # Enforce Nominatim 1 req/sec policy
    now = time.time()
    elapsed = now - _LAST_REQUEST_TIME
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    _LAST_REQUEST_TIME = time.time()
    
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": limit
    }
    
    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data:
                results.append({
                    "display_name": item.get("display_name", ""),
                    "name": item.get("display_name", "").split(",")[0],
                    "lat": float(item["lat"]),
                    "lon": float(item["lon"]),
                    "place_type": item.get("type", "location")
                })
            _GEOCODE_CACHE[q] = results
            return results
    except Exception as e:
        print(f"[WARN] Nominatim geocode error: {e}")
        
    return []
