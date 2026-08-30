import numpy as np
from geopy.distance import geodesic

def build_distance_matrix(nodes, graph=None, speed_kmh=50.0):
    """
    Computes NxN travel distance (km) and travel time (hours) matrices for nodes.
    Uses NetworkX graph shortest paths if provided, else accurate Geodesic distance as fallback.
    """
    n = len(nodes)
    dist_matrix = np.zeros((n, n))
    time_matrix = np.zeros((n, n))
    
    # Fast path if graph is provided
    if graph is not None:
        try:
            import osmnx as ox
            import networkx as nx
            
            node_ids = []
            for node in nodes:
                lat, lon = node['coords']
                # find nearest OSM node
                osm_node = ox.distance.nearest_nodes(graph, X=lon, Y=lat)
                node_ids.append(osm_node)
                
            for i in range(n):
                for j in range(n):
                    if i != j:
                        try:
                            length_m = nx.shortest_path_length(graph, node_ids[i], node_ids[j], weight='length')
                            dist_km = length_m / 1000.0
                            # Check travel time weight if calculated
                            try:
                                travel_time_sec = nx.shortest_path_length(graph, node_ids[i], node_ids[j], weight='travel_time')
                                time_hrs = travel_time_sec / 3600.0
                            except Exception:
                                time_hrs = dist_km / speed_kmh
                        except nx.NetworkXNoPath:
                            dist_km = geodesic(nodes[i]['coords'], nodes[j]['coords']).km * 1.3
                            time_hrs = dist_km / speed_kmh
                            
                        dist_matrix[i][j] = dist_km
                        time_matrix[i][j] = time_hrs
                        
            return dist_matrix, time_matrix
        except Exception as e:
            print(f"[WARN] Graph distance matrix computation failed ({e}), falling back to Geodesic.")
            
    # Geodesic fallback (with 1.25 road curvature multiplier)
    for i in range(n):
        for j in range(n):
            if i != j:
                d_km = geodesic(nodes[i]['coords'], nodes[j]['coords']).km * 1.25
                t_hrs = d_km / speed_kmh
                dist_matrix[i][j] = d_km
                time_matrix[i][j] = t_hrs
                
    try:
        from backend.maps.traffic_adjustment import apply_real_traffic
        time_matrix = apply_real_traffic(time_matrix, nodes)
    except Exception:
        pass  # keep the existing matrix unmodified on any failure

    return dist_matrix, time_matrix
