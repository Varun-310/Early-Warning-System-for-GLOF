"""
GLOF Prediction API - FastAPI Application

Provides REST API endpoints for:
- Real-time GLOF prediction
- Sensor data retrieval
- Emergency alert triggering
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn

from config import settings
from prediction_service import get_predictor
from alert_service import send_sms_alert, prepare_alert_data

# Create FastAPI app
app = FastAPI(
    title="GLOF Prediction API",
    description="API for Glacial Lake Outburst Flood prediction and alerting",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================
# Request/Response Models
# ========================

class SensorData(BaseModel):
    """Sensor data input for prediction."""
    Lake_Size_km2: Optional[float] = None
    Water_Level_m: Optional[float] = None
    Air_Temperature_C: Optional[float] = None
    Flow_Rate_m3_per_s: Optional[float] = None
    Ground_Movement_mm: Optional[float] = None
    Dam_Pressure_MPa: Optional[float] = None
    Precipitation_mm: Optional[float] = None
    Sensor_Accuracy_percent: Optional[float] = None
    Lake_Perimeter_Change_m: Optional[float] = None
    Snowpack_Thickness_m: Optional[float] = None
    Soil_Moisture_Content_percent: Optional[float] = None
    Solar_Radiation_W_per_m2: Optional[float] = None
    Water_Temperature_C: Optional[float] = None
    Water_Turbidity_NTU: Optional[float] = None
    Wind_Speed_m_per_s: Optional[float] = None
    Rainfall_mm: Optional[float] = None
    Snowfall_mm: Optional[float] = None


class AlertRequest(BaseModel):
    """Request to send emergency alert."""
    latitude: float
    longitude: float
    custom_message: Optional[str] = None


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""
    probability: float
    risk_level: str
    risk_message: str
    top_contributing_factors: List[str]
    sensor_values: Dict[str, float]


# ========================
# API Endpoints
# ========================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "GLOF Prediction API",
        "version": "1.0.0"
    }


@app.get("/api/predict", response_model=PredictionResponse)
async def get_prediction():
    """
    Get GLOF prediction using simulated sensor data.
    
    Returns current probability, risk level, and contributing factors.
    """
    predictor = get_predictor()
    result = predictor.predict()
    return result


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_with_data(sensor_data: SensorData):
    """
    Get GLOF prediction using provided sensor data.
    
    Provide partial or complete sensor readings for prediction.
    """
    predictor = get_predictor()
    
    # Convert to dict and rename fields with special characters
    data = sensor_data.dict(exclude_none=True)
    
    # Map field names back to model expected format
    field_mapping = {
        "Sensor_Accuracy_percent": "Sensor_Accuracy_%",
        "Soil_Moisture_Content_percent": "Soil_Moisture_Content_%"
    }
    
    for old_key, new_key in field_mapping.items():
        if old_key in data:
            data[new_key] = data.pop(old_key)
    
    # If partial data provided, merge with baseline
    if data:
        baseline = predictor.sensor_baseline.copy()
        baseline.update(data)
        result = predictor.predict(baseline)
    else:
        result = predictor.predict()
    
    return result


@app.get("/api/sensors")
async def get_sensor_values():
    """
    Get current simulated sensor values.
    
    Returns all sensor readings used for prediction.
    """
    predictor = get_predictor()
    values = predictor.generate_sensor_values()
    return {
        "sensors": values,
        "count": len(values)
    }


@app.post("/api/alert/preview")
async def preview_alert(request: AlertRequest):
    """
    Preview alert data without sending SMS.
    
    Returns what would be sent in an actual alert.
    """
    predictor = get_predictor()
    prediction = predictor.predict()
    
    alert_data = prepare_alert_data(
        probability=prediction["probability"],
        coordinates=(request.latitude, request.longitude)
    )
    
    return {
        "prediction": prediction,
        "alert": alert_data
    }


@app.post("/api/alert/send")
async def send_alert(request: AlertRequest):
    """
    Send emergency SMS alert.
    
    Sends SMS to all configured phone numbers with evacuation information.
    """
    predictor = get_predictor()
    prediction = predictor.predict()
    
    # Build alert message
    message = request.custom_message or (
        f"⚠️ GLOF ALERT! Risk Probability: {prediction['probability']}%\n"
        f"Risk Level: {prediction['risk_level']}\n"
        f"Immediate evacuation recommended!"
    )
    
    result = send_sms_alert(
        message=message,
        current_coordinates=(request.latitude, request.longitude)
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to send alert"))
    
    return {
        "status": "sent",
        "prediction": prediction,
        "alert_result": result
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
