import os
import pandas as pd

PRESET_LOCATIONS = {
    "manhattan-core": {
        "name": "Manhattan Core",
        "start": {"name": "Empire State Building, NY", "coords": (40.748817, -73.985428)},
        "csv": "demo_stops.csv"
    },
    "london-grid": {
        "name": "London Grid",
        "start": {"name": "Tower Bridge, London", "coords": (51.5055, -0.0754)},
        "csv": "demo_stops.csv"
    },
    "tokyo-hub": {
        "name": "Tokyo Hub",
        "start": {"name": "Tokyo Station, Tokyo", "coords": (35.6812, 139.7671)},
        "csv": "demo_stops.csv"
    }
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

def load_preset_stops(preset_id="manhattan-core"):
    """
    Loads stops dataset for predefined quick-start presets.
    """
    preset = PRESET_LOCATIONS.get(preset_id, PRESET_LOCATIONS["manhattan-core"])
    csv_file = preset["csv"]
    csv_path = os.path.join(DATA_DIR, csv_file)
    
    stops = []
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            stops.append({
                "name": str(row['name']),
                "coords": (float(row['lat']), float(row['lon'])),
                "window": (float(row.get('start_time', 8.0)), float(row.get('end_time', 18.0)))
            })
            
    return preset["start"], stops
