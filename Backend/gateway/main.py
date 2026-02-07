"""
GLOF System API Gateway
Unified entry point for all backend services.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from typing import Optional

app = FastAPI(
    title="GLOF Monitoring System API",
    description="Unified API Gateway for GLOF prediction and monitoring",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service endpoints
SERVICES = {
    "glof": "http://localhost:8001",
    "sar": "http://localhost:8002",
    "lake": "http://localhost:8003",
    "terrain": "http://localhost:8004"
}


@app.get("/")
async def root():
    """Health check and service status."""
    return {
        "status": "running",
        "service": "GLOF API Gateway",
        "version": "2.0.0",
        "services": list(SERVICES.keys())
    }


@app.get("/api/status")
async def get_all_status():
    """Get status of all backend services."""
    status = {}
    async with httpx.AsyncClient(timeout=2.0) as client:
        for name, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/")
                status[name] = {"status": "online", "data": response.json()}
            except:
                status[name] = {"status": "offline"}
    return status


# ========== GLOF Routes ==========

@app.get("/api/glof/predict")
async def glof_predict():
    """Get current GLOF prediction."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{SERVICES['glof']}/api/predict")
            return response.json()
        except:
            return {"error": "GLOF service unavailable", "mock": True, **MOCK_GLOF}


@app.get("/api/glof/sensors")
async def glof_sensors():
    """Get current sensor values."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{SERVICES['glof']}/api/sensors")
            return response.json()
        except:
            return {"error": "GLOF service unavailable", "mock": True, **MOCK_SENSORS}


# ========== SAR Routes ==========

@app.post("/api/sar/analyze")
async def sar_analyze(request: Request):
    """Analyze SAR image."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.body()
            content_type = request.headers.get("content-type", "")
            response = await client.post(
                f"{SERVICES['sar']}/api/analyze",
                content=body,
                headers={"content-type": content_type}
            )
            return response.json()
        except:
            return {"error": "SAR service unavailable", "mock": True, **MOCK_SAR}


# ========== Lake Routes ==========

@app.post("/api/lake/analyze")
async def lake_analyze(request: Request):
    """Analyze lake satellite image."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.body()
            content_type = request.headers.get("content-type", "")
            response = await client.post(
                f"{SERVICES['lake']}/api/analyze",
                content=body,
                headers={"content-type": content_type}
            )
            return response.json()
        except:
            return {"error": "Lake service unavailable", "mock": True, **MOCK_LAKE}


# ========== Terrain Routes ==========

@app.post("/api/terrain/dem/analyze")
async def terrain_dem_analyze(request: Request):
    """Analyze DEM data."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            body = await request.body()
            content_type = request.headers.get("content-type", "")
            response = await client.post(
                f"{SERVICES['terrain']}/api/dem/analyze",
                content=body,
                headers={"content-type": content_type}
            )
            return response.json()
        except:
            return {"error": "Terrain service unavailable", "mock": True, **MOCK_DEM}


@app.post("/api/terrain/motion/analyze")
async def terrain_motion_analyze(request: Request):
    """Analyze motion in video."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            body = await request.body()
            content_type = request.headers.get("content-type", "")
            response = await client.post(
                f"{SERVICES['terrain']}/api/motion/analyze-video",
                content=body,
                headers={"content-type": content_type}
            )
            return response.json()
        except:
            return {"error": "Terrain service unavailable", "mock": True, **MOCK_MOTION}


# ========== Mock Data ==========

MOCK_GLOF = {
    "probability": 23.5,
    "risk_level": "MODERATE",
    "confidence": 87.2,
    "timestamp": "2026-02-07T10:00:00Z"
}

MOCK_SENSORS = {
    "lake_size_km2": 1.52,
    "water_level_m": 10.3,
    "temperature_c": 14.7,
    "flow_rate_m3s": 105.2,
    "ground_movement_mm": 2.1,
    "dam_pressure_mpa": 1.02,
    "precipitation_mm": 48.5
}

MOCK_SAR = {
    "success": True,
    "predicted_class": "pre_glof",
    "confidence": 78.5,
    "glof_probability": 15.2,
    "risk_level": "LOW"
}

MOCK_LAKE = {
    "success": True,
    "lake": {"size_before_m2": 15000, "size_after_m2": 15200, "change_percent": 1.3},
    "ice": {"size_before_m2": 8000, "size_after_m2": 7800, "change_percent": -2.5},
    "risk": {"level": "LOW", "message": "Lake conditions stable"}
}

MOCK_DEM = {
    "success": True,
    "water_flow": {"submerged_area_m2": 5000, "overflow_rate_m3_per_s": 250},
    "risk": {"level": "MODERATE", "message": "Moderate water flow"}
}

MOCK_MOTION = {
    "success": True,
    "analysis": {"frames_analyzed": 50, "avg_flow_volume_m3": 2.5},
    "risk": {"level": "LOW", "message": "Normal water motion"}
}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
