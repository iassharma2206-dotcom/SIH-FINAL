import os
import hashlib
import numpy as np
try:
    import osmnx as ox
except ImportError:
    ox = None

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cached_graphs")
os.makedirs(CACHE_DIR, exist_ok=True)

def load_bbox_graph(points, pad_km=2.0):
    """
    Loads or fetches a scoped OSMnx graph covering points with padding.
    Caches graph locally as GraphML to avoid repeated Overpass calls.
    """
    if not points or ox is None:
        return None, 0, 0
        
    lats = [p['lat'] if isinstance(p, dict) else p[0] for p in points]
    lons = [p['lon'] if isinstance(p, dict) else p[1] for p in points]
    
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    # Pad bbox by ~pad_km (1 deg lat ~ 111km)
    lat_pad = pad_km / 111.0
    lon_pad = pad_km / (111.0 * max(0.1, abs(np.cos(np.radians(min_lat))))) if 'np' in globals() else pad_km / 111.0
    
    bbox_str = f"{round(min_lat - lat_pad, 3)},{round(max_lat + lat_pad, 3)},{round(min_lon - lon_pad, 3)},{round(max_lon + lon_pad, 3)}"
    graph_hash = hashlib.md5(bbox_str.encode('utf-8')).hexdigest()[:12]
    cache_path = os.path.join(CACHE_DIR, f"bbox_{graph_hash}.graphml")
    
    if os.path.exists(cache_path):
        try:
            G = ox.load_graphml(cache_path)
            return G, len(G.nodes), len(G.edges)
        except Exception as e:
            print(f"[WARN] Failed loading cached graphml: {e}")
            
    # Live fetch via OSMnx graph_from_bbox
    try:
        north, south = max_lat + lat_pad, min_lat - lat_pad
        east, west = max_lon + lon_pad, min_lon - lon_pad
        
        G = ox.graph_from_bbox(
            bbox=(north, south, east, west),
            network_type="drive",
            custom_filter='["highway"~"motorway|trunk|primary|secondary"]'
        )
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)
        
        # Save to cache
        try:
            ox.save_graphml(G, cache_path)
        except Exception as e:
            print(f"[WARN] Could not save graphml cache: {e}")
            
        return G, len(G.nodes), len(G.edges)
    except Exception as e:
        print(f"[WARN] Live bbox graph fetch failed ({e}), returning synthetic grid fallback.")
        return None, 0, 0
