from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.maps.osm_graph_bbox import load_bbox_graph
from backend.maps.osm_graph import load_preset_stops

router = APIRouter(prefix="/api/graph", tags=["Graph"])

class BboxRequest(BaseModel):
    points: List[dict] # [{lat, lon}]
    pad_km: Optional[float] = 2.0

@router.post("/load-bbox")
def load_bbox(req: BboxRequest):
    """
    Loads or fetches scoped OSMnx graph covering coordinates.
    """
    G, n_nodes, n_edges = load_bbox_graph(req.points, pad_km=req.pad_km or 2.0)
    return {
        "status": "success",
        "nodes_count": n_nodes,
        "edges_count": n_edges,
        "cached": G is not None
    }

@router.post("/load")
def load_preset(preset: str = "manhattan-core"):
    start, stops = load_preset_stops(preset)
    return {
        "preset": preset,
        "start": start,
        "stops_count": len(stops)
    }
