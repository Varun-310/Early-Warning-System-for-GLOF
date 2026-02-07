"""
SAR Image Analysis API - FastAPI Application

Provides REST API endpoints for:
- SAR image upload and analysis
- GLOF probability prediction
- Batch image analysis
- Firebase integration
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from config import settings
from sar_service import get_analyzer

# Create FastAPI app
app = FastAPI(
    title="SAR Image Analysis API",
    description="API for analyzing SAR satellite images to detect GLOF events",
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

# Create uploads directory
UPLOAD_DIR = settings.BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# ========================
# Request/Response Models
# ========================

class AnalyzePathRequest(BaseModel):
    """Request to analyze image from file path."""
    image_path: str


class BatchAnalyzeRequest(BaseModel):
    """Request to analyze multiple images."""
    image_paths: List[str]


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""
    success: bool
    predicted_class: Optional[str] = None
    confidence: Optional[float] = None
    probabilities: Optional[dict] = None
    glof_probability: Optional[float] = None
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ========================
# API Endpoints
# ========================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "SAR Image Analysis API",
        "version": "1.0.0",
        "model_loaded": get_analyzer().model is not None
    }


@app.post("/api/analyze", response_model=PredictionResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze uploaded SAR image for GLOF detection.
    
    Upload a SAR satellite image (JPG, PNG, TIF) to get GLOF prediction.
    """
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file bytes
        contents = await file.read()
        
        # Analyze image
        analyzer = get_analyzer()
        result = analyzer.predict_from_bytes(contents)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/path", response_model=PredictionResponse)
async def analyze_image_from_path(request: AnalyzePathRequest):
    """
    Analyze SAR image from file path on server.
    
    Provide the path to a SAR image on the server for analysis.
    """
    # Validate path exists
    image_path = Path(request.image_path)
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Image not found: {request.image_path}")
    
    try:
        analyzer = get_analyzer()
        result = analyzer.predict(str(image_path))
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/batch")
async def analyze_batch(request: BatchAnalyzeRequest):
    """
    Analyze multiple SAR images and get aggregated results.
    
    Provide a list of image paths for batch analysis.
    """
    if not request.image_paths:
        raise HTTPException(status_code=400, detail="No image paths provided")
    
    # Validate all paths exist
    for path in request.image_paths:
        if not Path(path).exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {path}")
    
    try:
        analyzer = get_analyzer()
        result = analyzer.analyze_batch(request.image_paths)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/sync-firebase")
async def analyze_and_sync(file: UploadFile = File(...)):
    """
    Analyze SAR image and send results to Firebase.
    
    Performs analysis and automatically syncs the prediction to Firebase.
    """
    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read and analyze
        contents = await file.read()
        analyzer = get_analyzer()
        prediction = analyzer.predict_from_bytes(contents)
        
        if not prediction.get("success"):
            return prediction
        
        # Sync to Firebase
        firebase_result = analyzer.send_to_firebase(prediction)
        
        return {
            **prediction,
            "firebase_sync": firebase_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dataset/info")
async def get_dataset_info():
    """
    Get information about the training dataset.
    
    Returns counts of images in each category.
    """
    data_dir = settings.DATA_DIR
    
    categories = {
        "pre_glof": data_dir / "Pre-glof",
        "during_glof": data_dir / "during-glof", 
        "post_glof": data_dir / "post-glof"
    }
    
    info = {}
    total = 0
    
    for category, path in categories.items():
        if path.exists():
            count = len([f for f in path.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.tif'}])
            info[category] = count
            total += count
        else:
            info[category] = 0
    
    return {
        "categories": info,
        "total_images": total,
        "data_directory": str(data_dir)
    }


@app.get("/api/model/info")
async def get_model_info():
    """
    Get information about the loaded model.
    """
    analyzer = get_analyzer()
    
    if analyzer.model is None:
        return {
            "loaded": False,
            "error": "Model not loaded"
        }
    
    return {
        "loaded": True,
        "model_path": str(settings.MODEL_PATH),
        "input_shape": str(analyzer.model.input_shape),
        "output_classes": len(settings.CLASS_LABELS),
        "class_labels": settings.CLASS_LABELS
    }


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
