"""
Configuration module for GLOF Prediction API.
Loads settings from environment variables.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Alert Recipients
    @property
    def ALERT_PHONE_NUMBERS(self) -> List[str]:
        numbers = os.getenv("ALERT_PHONE_NUMBERS", "")
        return [n.strip() for n in numbers.split(",") if n.strip()]
    
    # Model Configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/glof_prediction_model.pkl")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Safe Locations for evacuation
    SAFE_LOCATIONS = [
        {"name": "Gaurikund", "coordinates": (30.6603, 79.0327)},
        {"name": "Sonprayag", "coordinates": (30.61171, 78.97866)},
        {"name": "Rudraprayag", "coordinates": (30.284414, 78.981140)},
    ]


settings = Settings()
