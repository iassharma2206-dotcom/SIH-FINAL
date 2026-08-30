import os
import sys
import io

# Force UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api import routes_geocode, routes_graph, routes_optimize, websocket

app = FastAPI(
    title="SIH26137 - Quantum-Inspired Intelligent Traffic Route Optimizer",
    version="2.0.0",
    description="QPSO Metaheuristic Framework for VRP & Shortest Path Routing"
)

# CORS configuration for frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(routes_geocode.router)
app.include_router(routes_graph.router)
app.include_router(routes_optimize.router)
app.include_router(websocket.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "system": "Quantum Route Optimizer API",
        "version": "2.0.0",
        "engine": "QPSO (Sun, Feng, Xu formulation)"
    }

# Mount static build folder if present
dist_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_p = os.path.join(dist_path, full_path)
        if os.path.exists(file_p) and os.path.isfile(file_p):
            return FileResponse(file_p)
        return FileResponse(os.path.join(dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
