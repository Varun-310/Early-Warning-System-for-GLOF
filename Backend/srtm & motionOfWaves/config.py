"""
Configuration for SRTM & Motion Detection API.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8004"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    STATIC_DIR: Path = BASE_DIR / "static"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # DEM Processing
    DEFAULT_DOWNSCALE_FACTOR: int = int(os.getenv("DEFAULT_DOWNSCALE_FACTOR", "5"))
    DEFAULT_WATER_LEVEL_THRESHOLD: int = int(os.getenv("DEFAULT_WATER_LEVEL_THRESHOLD", "90"))
    
    # Motion Detection
    PIXEL_TO_METER_CONVERSION: float = float(os.getenv("PIXEL_TO_METER_CONVERSION", "0.01"))
    ESTIMATED_DEPTH: float = float(os.getenv("ESTIMATED_DEPTH", "0.5"))
    MOTION_THRESHOLD: float = float(os.getenv("MOTION_THRESHOLD", "1.5"))
    
    # Glacial lake color ranges (HSV)
    GLACIAL_LAKE_COLORS = [
        ((75, 50, 50), (120, 255, 255)),   # Turquoise/Blue-Green
        ((100, 50, 50), (140, 255, 255)),  # Deep Blue
        ((60, 50, 50), (80, 255, 255)),    # Emerald Green
        ((90, 20, 150), (120, 100, 255))   # Milky Blue/Grayish Blue
    ]


settings = Settings()

# Create directories
settings.STATIC_DIR.mkdir(exist_ok=True)
settings.UPLOAD_DIR.mkdir(exist_ok=True)
