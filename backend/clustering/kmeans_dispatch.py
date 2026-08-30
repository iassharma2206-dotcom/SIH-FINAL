import numpy as np
from sklearn.cluster import KMeans

def cluster_stops_for_fleet(stops_data, n_vehicles=1):
    """
    K-Means clustering to partition stops across fleet vehicles based on geospatial location.
    Returns: list of stop clusters (one per vehicle)
    """
    if n_vehicles <= 1 or len(stops_data) <= 1:
        return [stops_data]
        
    k = min(n_vehicles, len(stops_data))
    coords = np.array([[s['coords'][0], s['coords'][1]] for s in stops_data])
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10).fit(coords)
    
    clusters = [[] for _ in range(k)]
    for idx, label in enumerate(kmeans.labels_):
        clusters[label].append(stops_data[idx])
        
    # Filter out empty clusters
    clusters = [c for c in clusters if len(c) > 0]
    return clusters
