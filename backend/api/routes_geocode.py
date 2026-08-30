from fastapi import APIRouter, Query
from backend.maps.geocode import search_location

router = APIRouter(prefix="/api/geocode", tags=["Geocode"])

@router.get("/search")
def geocode_search(q: str = Query(..., min_length=2)):
    """
    Global search-as-you-type autocomplete using OpenStreetMap Nominatim.
    """
    results = search_location(q, limit=5)
    return {"query": q, "results": results}
