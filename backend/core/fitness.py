import numpy as np

def calculate_route_fitness(route_indices, dist_matrix, time_matrix, nodes, start_time_hour=8.0):
    """
    Fitness Function:
    fitness(route) = total_travel_time(route) + time_window_penalty(route) + traffic_penalty
    
    Lower value = better fitness.
    """
    total_travel_time_hours = 0.0
    total_distance_km = 0.0
    current_time = start_time_hour
    time_window_penalty = 0.0
    
    for i in range(len(route_indices) - 1):
        u, v = route_indices[i], route_indices[i+1]
        
        d_km = dist_matrix[u][v]
        t_hrs = time_matrix[u][v]
        
        total_distance_km += d_km
        total_travel_time_hours += t_hrs
        current_time += t_hrs
        
        # Check Time Window constraint if node 'v' has time window [start, end]
        if v < len(nodes) and 'window' in nodes[v] and nodes[v]['window']:
            start_w, end_w = nodes[v]['window']
            if current_time < start_w:
                # Arrived early -> wait until start window
                current_time = start_w
            elif current_time > end_w:
                # Overdue penalty: 1 hour late = 50.0 penalty cost
                overdue = current_time - end_w
                time_window_penalty += overdue * 50.0

    total_fitness = total_travel_time_hours * 60.0 + time_window_penalty * 60.0 # converted to minutes equivalent cost
    return total_fitness, total_distance_km, total_travel_time_hours * 60.0, time_window_penalty
