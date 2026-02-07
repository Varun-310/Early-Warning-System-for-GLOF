"""
SRTM & Motion Detection API - FastAPI Application

Provides REST API endpoints for:
- DEM (Digital Elevation Model) water flow analysis
- Video/image motion detection for water flow
- Flood risk assessment
"""
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from config import settings
from dem_service import get_dem_analyzer
from motion_service import get_motion_detector

# Create FastAPI app
app = FastAPI(
    title="SRTM & Motion Detection API",
    description="API for DEM water flow analysis and motion detection in glacial lakes",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")


# ========================
# Request Models
# ========================

class DEMAnalyzeRequest(BaseModel):
    """Request to analyze DEM from path."""
    dem_path: str
    downscale_factor: Optional[int] = 5
    water_level_threshold: Optional[int] = 90


class VideoAnalyzeRequest(BaseModel):
    """Request to analyze video from path."""
    video_path: str
    max_frames: Optional[int] = 100
    frame_skip: Optional[int] = 1


# ========================
# API Endpoints
# ========================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "SRTM & Motion Detection API",
        "version": "1.0.0"
    }


# ----- DEM Analysis Endpoints -----

@app.post("/api/dem/analyze")
async def analyze_dem_upload(
    file: UploadFile = File(...),
    downscale_factor: int = Form(default=5),
    water_level_threshold: int = Form(default=90)
):
    """
    Analyze uploaded DEM (GeoTIFF) file for water flow.
    
    - **file**: DEM GeoTIFF file
    - **downscale_factor**: Reduce resolution (higher = faster)
    - **water_level_threshold**: Percentile for water detection
    """
    if not file.filename.lower().endswith(('.tif', '.tiff')):
        raise HTTPException(400, "File must be a GeoTIFF (.tif)")
    
    try:
        contents = await file.read()
        analyzer = get_dem_analyzer()
        result = analyzer.analyze_dem(
            dem_bytes=contents,
            downscale_factor=downscale_factor,
            water_level_threshold=water_level_threshold
        )
        return result
        
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/dem/analyze/path")
async def analyze_dem_from_path(request: DEMAnalyzeRequest):
    """
    Analyze DEM from server file path.
    """
    if not Path(request.dem_path).exists():
        raise HTTPException(404, f"DEM file not found: {request.dem_path}")
    
    try:
        analyzer = get_dem_analyzer()
        result = analyzer.analyze_dem(
            dem_path=request.dem_path,
            downscale_factor=request.downscale_factor,
            water_level_threshold=request.water_level_threshold
        )
        return result
        
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/dem/visualize")
async def visualize_dem(
    file: UploadFile = File(...)
):
    """
    Generate visualization of DEM with water flow.
    
    Returns PNG image showing elevation, flow, and submerged areas.
    """
    if not file.filename.lower().endswith(('.tif', '.tiff')):
        raise HTTPException(400, "File must be a GeoTIFF (.tif)")
    
    try:
        # Save temporarily for rasterio
        import tempfile
        contents = await file.read()
        
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as f:
            f.write(contents)
            temp_path = f.name
        
        analyzer = get_dem_analyzer()
        image_bytes = analyzer.generate_visualization(dem_path=temp_path)
        
        import os
        os.unlink(temp_path)
        
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=dem_visualization.png"}
        )
        
    except Exception as e:
        raise HTTPException(500, str(e))


# ----- Motion Detection Endpoints -----

@app.post("/api/motion/analyze-pair")
async def analyze_motion_pair(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...)
):
    """
    Analyze motion between two consecutive images.
    
    Upload two frames from a time series to detect water flow motion.
    """
    try:
        bytes1 = await image1.read()
        bytes2 = await image2.read()
        
        detector = get_motion_detector()
        result = detector.analyze_image_pair(bytes1, bytes2)
        return result
        
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/motion/analyze-video/path")
async def analyze_video_from_path(request: VideoAnalyzeRequest):
    """
    Analyze video from server path for water flow motion.
    """
    if not Path(request.video_path).exists():
        raise HTTPException(404, f"Video not found: {request.video_path}")
    
    try:
        detector = get_motion_detector()
        result = detector.analyze_video(
            video_path=request.video_path,
            max_frames=request.max_frames,
            frame_skip=request.frame_skip
        )
        return result
        
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/motion/analyze-video")
async def analyze_video_upload(
    file: UploadFile = File(...),
    max_frames: int = Form(default=100),
    frame_skip: int = Form(default=1)
):
    """
    Analyze uploaded video for water flow motion.
    
    - **file**: Video file (MP4, AVI, etc.)
    - **max_frames**: Maximum frames to analyze
    - **frame_skip**: Process every Nth frame
    """
    try:
        # Save video temporarily
        import tempfile
        contents = await file.read()
        
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(contents)
            temp_path = f.name
        
        detector = get_motion_detector()
        result = detector.analyze_video(
            video_path=temp_path,
            max_frames=max_frames,
            frame_skip=frame_skip
        )
        
        import os
        os.unlink(temp_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(500, str(e))


# ========================
# Run Server
# ========================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
