"""
Configuration for Lake Size Analysis API.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8003"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    STATIC_DIR: Path = BASE_DIR / "static"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # Image Processing Parameters
    DEFAULT_RESOLUTION: int = int(os.getenv("DEFAULT_RESOLUTION", "10"))  # meters per pixel
    DILATION_LAKE: int = int(os.getenv("DILATION_LAKE", "5"))  # dilation disk size for lake
    DILATION_ICE: int = int(os.getenv("DILATION_ICE", "3"))  # dilation disk size for ice


settings = Settings()

# Create directories
settings.STATIC_DIR.mkdir(exist_ok=True)
settings.UPLOAD_DIR.mkdir(exist_ok=True)
