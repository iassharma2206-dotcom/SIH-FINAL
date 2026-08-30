"""
backend/maps/road_path.py
Streamlit-free extraction of road geometry fetching and routing tiers.
Priority: TomTom API -> OSRM API -> Local OSMnx Graph -> Geodesic Fallback
"""
import os
import requests
import logging
from geopy.distance import geodesic

logger = logging.getLogger("backend_road_path")


def _get_tomtom_key():
    """Retrieve TomTom API key from environment, config, or .env without streamlit dependency."""
    key = os.environ.get("TOMTOM_API_KEY")
    if key and key != "your_tomtom_api_key_here":
        return key

    try:
        from config import TOMTOM_API_KEY as CONFIG_KEY
        if CONFIG_KEY and CONFIG_KEY != "your_tomtom_api_key_here":
            return CONFIG_KEY
    except Exception:
        pass

    try:
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
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


def get_road_path(coords):
    """
    Fetches real road geometry.
    Priority: TomTom API -> OSRM API -> Local OSMnx Graph -> Geodesic Fallback
    Returns: (path_geometry, distance_km, duration_mins, is_fallback)
    """
    if len(coords) < 2:
        return coords, 0.0, 0.0, False

    tomtom_key = _get_tomtom_key()
    
    # ── Tier 1: TomTom Routing API ──────────────────────────────────────
    if tomtom_key:
        try:
            loc_string = ":".join([f"{lat},{lon}" for lat, lon in coords])
            url = f"https://api.tomtom.com/routing/1/calculateRoute/{loc_string}/json"
            params = {"key": tomtom_key, "traffic": "true", "routeType": "fastest"}
            r = requests.get(url, params=params, timeout=5)
            if r.status_code == 200:
                data = r.json()
                routes = data.get("routes", [])
                if routes:
                    summary = routes[0]["summary"]
                    legs = routes[0]["legs"]
                    points = []
                    for leg in legs:
                        for p in leg["points"]:
                            points.append([p["latitude"], p["longitude"]])
                    dist_km = summary["lengthInMeters"] / 1000.0
                    time_mins = summary["travelTimeInSeconds"] / 60.0
                    logger.info(f"[TomTom Routing OK] Fetched {len(points)} geometry points. Dist: {dist_km:.2f}km")
                    return points, dist_km, time_mins, False
            else:
                logger.warning(f"[TomTom Routing Failed] HTTP {r.status_code}: {r.text[:150]}")
        except Exception as e:
            logger.warning(f"[TomTom Routing Exception] {e}")
    else:
        logger.info("[TomTom Routing Skipped] No TOMTOM_API_KEY environment variable set.")

    # ── Tier 2: OSRM Routing API ────────────────────────────────────────
    loc_string = ";".join([f"{lon},{lat}" for lat, lon in coords])
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{loc_string}?overview=full&geometries=geojson"
    try:
        r = requests.get(osrm_url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if 'routes' in data and len(data['routes']) > 0:
                rt = data['routes'][0]
                geometry = rt['geometry']['coordinates']
                # OSRM returns [lon, lat], Folium/Leaflet needs [lat, lon]
                path_geo = [[p[1], p[0]] for p in geometry]
                dist_km = rt['distance'] / 1000.0
                time_mins = rt['duration'] / 60.0
                logger.info(f"[OSRM Routing OK] Fetched {len(path_geo)} geometry points. Dist: {dist_km:.2f}km")
                return path_geo, dist_km, time_mins, False
            else:
                logger.warning(f"[OSRM Routing Failed] Response missing routes array: {data}")
        else:
            logger.warning(f"[OSRM Routing Failed] HTTP {r.status_code}: {r.text[:150]}")
    except Exception as e:
        logger.warning(f"[OSRM Routing Exception] {e}")

    # ── Tier 3: Local OSMnx Shortest Path Routing ───────────────────────
    try:
        from backend.maps.osm_graph_bbox import load_bbox_graph
        import osmnx as ox
        import networkx as nx
        
        G, num_nodes, _ = load_bbox_graph(coords, pad_km=3.0)
        if G is not None and num_nodes > 0:
            points = []
            total_len_m = 0.0
            for i in range(len(coords) - 1):
                c1, c2 = coords[i], coords[i+1]
                orig = ox.distance.nearest_nodes(G, c1[1], c1[0])
                dest = ox.distance.nearest_nodes(G, c2[1], c2[0])
                route_nodes = nx.shortest_path(G, orig, dest, weight='length')
                for node in route_nodes:
                    points.append([G.nodes[node]['y'], G.nodes[node]['x']])
                for u, v in zip(route_nodes[:-1], route_nodes[1:]):
                    edge_data = G.get_edge_data(u, v)
                    if edge_data and 0 in edge_data:
                        total_len_m += edge_data[0].get('length', 0)
            
            dist_km = total_len_m / 1000.0 if total_len_m > 0 else sum(geodesic(coords[i], coords[i+1]).km for i in range(len(coords)-1))
            time_mins = (dist_km / 45.0) * 60.0
            if points:
                logger.info(f"[OSMnx Local Graph Routing OK] Computed {len(points)} points via NetworkX.")
                return points, dist_km, time_mins, False
    except Exception as e:
        logger.warning(f"[OSMnx Local Graph Routing Exception] {e}")

    # ── Tier 4: Honest Geodesic Straight-Line Fallback ──────────────────
    logger.error("[All Road Routing Sources Failed] Falling back to honest geodesic straight line calculation.")
    total_dist_km = 0.0
    for i in range(len(coords) - 1):
        total_dist_km += geodesic(coords[i], coords[i+1]).km
    
    total_time_mins = (total_dist_km / 45.0) * 60.0
    return coords, total_dist_km, total_time_mins, True
