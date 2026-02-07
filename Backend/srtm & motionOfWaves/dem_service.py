"""
DEM (Digital Elevation Model) Analysis Service.
Analyzes SRTM/DEM data for water flow and submerged area detection.
"""
import io
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

from config import settings


class DEMAnalyzer:
    """Analyzes DEM data for water flow patterns and flood risk."""
    
    def __init__(
        self, 
        downscale_factor: int = None,
        water_level_threshold: int = None
    ):
        """
        Initialize DEM analyzer.
        
        Args:
            downscale_factor: Factor to reduce DEM resolution (higher = faster but less accurate)
            water_level_threshold: Percentile for water level detection
        """
        self.downscale_factor = downscale_factor or settings.DEFAULT_DOWNSCALE_FACTOR
        self.water_level_threshold = water_level_threshold or settings.DEFAULT_WATER_LEVEL_THRESHOLD
    
    def analyze_dem(
        self,
        dem_path: Union[str, Path] = None,
        dem_bytes: bytes = None,
        downscale_factor: int = None,
        water_level_threshold: int = None
    ) -> Dict[str, Any]:
        """
        Analyze DEM file for water flow and flood risk.
        
        Args:
            dem_path: Path to GeoTIFF DEM file
            dem_bytes: Raw bytes of DEM file
            downscale_factor: Override default downscale factor
            water_level_threshold: Override default water level threshold
            
        Returns:
            Analysis results with flow metrics
        """
        try:
            import rasterio
        except ImportError:
            return {"success": False, "error": "rasterio not installed"}
        
        downscale = downscale_factor or self.downscale_factor
        threshold = water_level_threshold or self.water_level_threshold
        
        try:
            # Load DEM
            if dem_bytes:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as f:
                    f.write(dem_bytes)
                    temp_path = f.name
                with rasterio.open(temp_path) as src:
                    dem_data = src.read(1).astype(float)
                    dem_data[dem_data == src.nodata] = np.nan
                import os
                os.unlink(temp_path)
            else:
                with rasterio.open(str(dem_path)) as src:
                    dem_data = src.read(1).astype(float)
                    dem_data[dem_data == src.nodata] = np.nan
            
            # Downsample
            dem_data = dem_data[::downscale, ::downscale]
            
            # Smooth
            dem_smoothed = gaussian_filter(dem_data, sigma=2)
            
            # Calculate flow direction and magnitude
            gradient_y, gradient_x = np.gradient(-dem_smoothed)
            flow_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            
            # Calculate water level threshold
            water_level = np.nanpercentile(dem_smoothed, threshold)
            water_mask = dem_smoothed <= water_level
            
            # Calculate metrics
            submerged_volume = float(np.nansum(water_mask * (water_level - dem_smoothed)))
            submerged_area = float(np.nansum(water_mask) * (downscale ** 2))
            overflow_rate = float(np.nansum(flow_magnitude * water_mask))
            avg_flow_velocity = float(np.nanmean(flow_magnitude))
            
            # Elevation stats
            min_elevation = float(np.nanmin(dem_data))
            max_elevation = float(np.nanmax(dem_data))
            mean_elevation = float(np.nanmean(dem_data))
            
            # Risk assessment
            risk_level, risk_message = self._assess_risk(
                submerged_area, overflow_rate, avg_flow_velocity
            )
            
            return {
                "success": True,
                "dimensions": {"height": dem_data.shape[0], "width": dem_data.shape[1]},
                "downscale_factor": downscale,
                "elevation": {
                    "min_m": round(min_elevation, 2),
                    "max_m": round(max_elevation, 2),
                    "mean_m": round(mean_elevation, 2),
                    "water_level_threshold_m": round(water_level, 2)
                },
                "water_flow": {
                    "submerged_volume_m3": round(submerged_volume, 2),
                    "submerged_area_m2": round(submerged_area, 2),
                    "overflow_rate_m3_per_s": round(overflow_rate, 2),
                    "avg_flow_velocity_m_per_s": round(avg_flow_velocity, 4)
                },
                "risk": {
                    "level": risk_level,
                    "message": risk_message
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _assess_risk(
        self, 
        submerged_area: float, 
        overflow_rate: float, 
        flow_velocity: float
    ) -> tuple:
        """Assess flood risk from DEM metrics."""
        if overflow_rate > 1000 or flow_velocity > 0.5:
            return "HIGH", "High water flow detected - Significant flood risk"
        elif overflow_rate > 500 or flow_velocity > 0.3:
            return "MODERATE", "Moderate water flow - Monitor conditions"
        else:
            return "LOW", "Normal water flow conditions"
    
    def generate_visualization(
        self,
        dem_path: Union[str, Path],
        output_path: str = None
    ) -> bytes:
        """
        Generate 2D visualization of DEM with water flow.
        
        Returns:
            PNG image bytes
        """
        try:
            import rasterio
            
            with rasterio.open(str(dem_path)) as src:
                dem_data = src.read(1).astype(float)
                dem_data[dem_data == src.nodata] = np.nan
            
            # Downsample
            dem_data = dem_data[::self.downscale_factor, ::self.downscale_factor]
            dem_smoothed = gaussian_filter(dem_data, sigma=2)
            
            # Calculate flow
            gradient_y, gradient_x = np.gradient(-dem_smoothed)
            flow_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            
            # Water mask
            water_level = np.nanpercentile(dem_smoothed, self.water_level_threshold)
            water_mask = dem_smoothed <= water_level
            
            # Create visualization
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Elevation
            im1 = axes[0].imshow(dem_data, cmap='terrain')
            axes[0].set_title("Elevation Map")
            plt.colorbar(im1, ax=axes[0], label="Elevation (m)")
            
            # Flow magnitude
            im2 = axes[1].imshow(flow_magnitude, cmap='Blues')
            axes[1].set_title("Flow Magnitude")
            plt.colorbar(im2, ax=axes[1], label="Velocity")
            
            # Submerged areas
            im3 = axes[2].imshow(water_mask, cmap='Blues')
            axes[2].set_title("Submerged Areas")
            
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(buf.getvalue())
            
            return buf.getvalue()
            
        except Exception as e:
            raise ValueError(f"Visualization failed: {e}")


# Global instance
_dem_analyzer = None


def get_dem_analyzer() -> DEMAnalyzer:
    """Get or create global DEM analyzer instance."""
    global _dem_analyzer
    if _dem_analyzer is None:
        _dem_analyzer = DEMAnalyzer()
    return _dem_analyzer
