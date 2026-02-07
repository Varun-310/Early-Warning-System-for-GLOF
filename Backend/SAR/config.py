"""
Configuration module for SAR Image Analysis API.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Firebase Configuration
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL", "")
    
    # Model Configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "glof_cnn_model.h5")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8002"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Image Processing
    IMAGE_SIZE: int = int(os.getenv("IMAGE_SIZE", "128"))
    
    # Data paths (cross-platform)
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Class labels for the 3-class model
    CLASS_LABELS = {
        0: "pre_glof",
        1: "during_glof", 
        2: "post_glof"
    }
    
    # Risk mappings for each class
    RISK_MAPPING = {
        "pre_glof": {"risk_level": "LOW", "risk_score": 25, "message": "Normal conditions - Pre-GLOF state"},
        "during_glof": {"risk_level": "CRITICAL", "risk_score": 95, "message": "GLOF IN PROGRESS - Immediate evacuation required!"},
        "post_glof": {"risk_level": "MODERATE", "risk_score": 50, "message": "Post-GLOF conditions - Monitor for secondary events"}
    }


settings = Settings()
