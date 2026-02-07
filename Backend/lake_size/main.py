"""
Lake Size Analysis API - FastAPI Application

Provides REST API endpoints for:
- Satellite image analysis for lake/ice coverage
- Image visualization generation
- Multi-image comparison and trend analysis
"""
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from config import settings
from lake_service import get_analyzer

# Create FastAPI app
app = FastAPI(
    title="Lake Size Analysis API",
    description="API for analyzing glacial lake size and ice coverage from satellite images",
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

class AnalyzePathRequest(BaseModel):
    """Request to analyze from file path."""
    image_path: str
    resolution: int = 10


class CompareRequest(BaseModel):
    """Request to compare multiple images."""
    image_paths: List[str]
    resolution: int = 10


# ========================
# API Endpoints
# ========================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Lake Size Analysis API",
        "version": "1.0.0"
    }


@app.post("/api/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    resolution: int = Form(default=10)
):
    """
    Analyze uploaded satellite image for lake and ice coverage.
    
    - **file**: Satellite image (JPG, PNG, TIF)
    - **resolution**: Meters per pixel (default: 10)
    """
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(400, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
    
    try:
        contents = await file.read()
        analyzer = get_analyzer()
        result = analyzer.analyze_image(image_bytes=contents, resolution=resolution)
        return result
        
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/analyze/path")
async def analyze_from_path(request: AnalyzePathRequest):
    """
    Analyze satellite image from server file path.
    """
    if not Path(request.image_path).exists():
        raise HTTPException(404, f"Image not found: {request.image_path}")
    
    try:
        analyzer = get_analyzer()
        result = analyzer.analyze_image(
            image_path=request.image_path, 
            resolution=request.resolution
        )
        return result
        
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/visualize")
async def generate_visualization(
    file: UploadFile = File(...)
):
    """
    Generate lake/ice detection visualization from uploaded image.
    
    Returns PNG image showing original, lake mask, and ice mask.
    """
    try:
        contents = await file.read()
        analyzer = get_analyzer()
        image_bytes = analyzer.generate_visualization(image_bytes=contents)
        
        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=visualization.png"}
        )
        
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/compare")
async def compare_images(request: CompareRequest):
    """
    Compare multiple satellite images and analyze trends.
    
    Provide images in chronological order for trend analysis.
    """
    # Validate all paths exist
    for path in request.image_paths:
        if not Path(path).exists():
            raise HTTPException(404, f"Image not found: {path}")
    
    try:
        analyzer = get_analyzer()
        result = analyzer.compare_images(
            image_paths=request.image_paths,
            resolution=request.resolution
        )
        return result
        
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/analyze/full")
async def analyze_with_visualization(
    file: UploadFile = File(...),
    resolution: int = Form(default=10)
):
    """
    Analyze image and return both results and visualization URL.
    """
    try:
        contents = await file.read()
        analyzer = get_analyzer()
        
        # Analyze
        result = analyzer.analyze_image(image_bytes=contents, resolution=resolution)
        
        # Generate and save visualization
        import uuid
        viz_filename = f"viz_{uuid.uuid4().hex[:8]}.png"
        viz_path = settings.STATIC_DIR / viz_filename
        analyzer.generate_visualization(image_bytes=contents, output_path=str(viz_path))
        
        result["visualization_url"] = f"/static/{viz_filename}"
        
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
