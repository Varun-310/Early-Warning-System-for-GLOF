"""
Lake Size Analysis Service.
Analyzes satellite images to detect glacial lake and ice coverage changes.
"""
import os
import io
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, Any, Union, List, Optional
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu
from skimage.morphology import dilation, disk
from skimage import measure

from config import settings


class LakeAnalyzer:
    """Analyzes glacial lake images for size and ice coverage changes."""
    
    def __init__(self, resolution: int = None):
        """
        Initialize analyzer.
        
        Args:
            resolution: Meters per pixel (default from settings)
        """
        self.resolution = resolution or settings.DEFAULT_RESOLUTION
    
    def analyze_image(
        self, 
        image_path: Union[str, Path] = None,
        image_bytes: bytes = None,
        resolution: int = None
    ) -> Dict[str, Any]:
        """
        Analyze a satellite image for lake and ice coverage.
        
        Args:
            image_path: Path to image file
            image_bytes: Raw image bytes (alternative to path)
            resolution: Override default resolution
            
        Returns:
            Analysis results dictionary
        """
        resolution = resolution or self.resolution
        
        # Load image
        if image_bytes:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif image_path:
            image = cv2.imread(str(image_path))
        else:
            raise ValueError("Either image_path or image_bytes must be provided")
        
        if image is None:
            raise ValueError("Could not read image")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Otsu's thresholding
        lake_threshold = threshold_otsu(gray)
        
        # Create binary masks
        lake_mask = gray <= lake_threshold
        ice_mask = gray > lake_threshold
        
        # Label regions
        lake_labeled = measure.label(lake_mask)
        ice_labeled = measure.label(ice_mask)
        
        # Calculate initial sizes
        lake_size_before = self._get_largest_region_size(lake_labeled)
        ice_size_before = self._get_largest_region_size(ice_labeled)
        
        # Convert to square meters
        lake_size_before_m2 = lake_size_before * (resolution ** 2)
        ice_size_before_m2 = ice_size_before * (resolution ** 2)
        
        # Apply dilation (simulating expansion prediction)
        dilated_lake = dilation(lake_mask, disk(settings.DILATION_LAKE))
        dilated_ice = dilation(ice_mask, disk(settings.DILATION_ICE))
        
        # Calculate dilated sizes
        lake_size_after = self._get_largest_region_size(measure.label(dilated_lake))
        ice_size_after = self._get_largest_region_size(measure.label(dilated_ice))
        
        lake_size_after_m2 = lake_size_after * (resolution ** 2)
        ice_size_after_m2 = ice_size_after * (resolution ** 2)
        
        # Calculate changes
        lake_change_percent = self._calculate_change_percent(lake_size_before_m2, lake_size_after_m2)
        ice_change_percent = self._calculate_change_percent(ice_size_before_m2, ice_size_after_m2)
        
        # Calculate totals
        total_area_m2 = image.shape[0] * image.shape[1] * (resolution ** 2)
        water_percentage = (lake_size_after_m2 / total_area_m2) * 100 if total_area_m2 > 0 else 0
        
        # Determine ice status
        ice_status = "No ice detected" if ice_size_after_m2 == 0 else f"{ice_size_after_m2:.2f} m²"
        
        # Determine risk based on lake expansion
        risk_level, risk_message = self._assess_risk(lake_change_percent, water_percentage)
        
        return {
            "success": True,
            "image_dimensions": {"height": image.shape[0], "width": image.shape[1]},
            "resolution_m_per_pixel": resolution,
            "lake": {
                "size_before_m2": round(lake_size_before_m2, 2),
                "size_after_m2": round(lake_size_after_m2, 2),
                "change_percent": round(lake_change_percent, 2),
            },
            "ice": {
                "size_before_m2": round(ice_size_before_m2, 2),
                "size_after_m2": round(ice_size_after_m2, 2),
                "change_percent": round(ice_change_percent, 2),
                "status": ice_status
            },
            "coverage": {
                "total_area_m2": round(total_area_m2, 2),
                "water_percentage": round(water_percentage, 2)
            },
            "risk": {
                "level": risk_level,
                "message": risk_message
            }
        }
    
    def _get_largest_region_size(self, labeled_image: np.ndarray) -> int:
        """Get the size of the largest labeled region."""
        props = measure.regionprops(labeled_image)
        return max([prop.area for prop in props]) if props else 0
    
    def _calculate_change_percent(self, before: float, after: float) -> float:
        """Calculate percentage change."""
        if before > 0:
            return ((after - before) / before) * 100
        return 0.0
    
    def _assess_risk(self, lake_change: float, water_percentage: float) -> tuple:
        """Assess risk based on lake metrics."""
        if lake_change > 20 or water_percentage > 60:
            return "HIGH", "Significant lake expansion detected - High GLOF risk"
        elif lake_change > 10 or water_percentage > 40:
            return "MODERATE", "Notable lake changes - Monitor closely"
        else:
            return "LOW", "Lake conditions stable"
    
    def generate_visualization(
        self,
        image_path: Union[str, Path] = None,
        image_bytes: bytes = None,
        output_path: str = None
    ) -> bytes:
        """
        Generate visualization of lake/ice masks.
        
        Returns:
            PNG image bytes
        """
        # Load image
        if image_bytes:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = cv2.imread(str(image_path))
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lake_threshold = threshold_otsu(gray)
        lake_mask = gray <= lake_threshold
        ice_mask = gray > lake_threshold
        
        # Create visualization
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Original
        axes[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        axes[0].set_title("Original Image")
        axes[0].axis('off')
        
        # Lake mask
        axes[1].imshow(lake_mask, cmap='Blues')
        axes[1].set_title("Lake Detection")
        axes[1].axis('off')
        
        # Ice mask
        axes[2].imshow(ice_mask, cmap='Greys')
        axes[2].set_title("Ice Detection")
        axes[2].axis('off')
        
        plt.tight_layout()
        
        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(buf.getvalue())
        
        return buf.getvalue()
    
    def compare_images(
        self,
        image_paths: List[str],
        resolution: int = None
    ) -> Dict[str, Any]:
        """
        Compare multiple images and track changes over time.
        
        Args:
            image_paths: List of image paths (chronological order)
            resolution: Meters per pixel
            
        Returns:
            Comparison results with trend analysis
        """
        resolution = resolution or self.resolution
        results = []
        
        for path in image_paths:
            result = self.analyze_image(image_path=path, resolution=resolution)
            result["image_path"] = str(path)
            results.append(result)
        
        # Calculate trends
        if len(results) >= 2:
            lake_sizes = [r["lake"]["size_after_m2"] for r in results if r.get("success")]
            
            if len(lake_sizes) >= 2:
                total_change = lake_sizes[-1] - lake_sizes[0]
                avg_change = total_change / (len(lake_sizes) - 1)
                trend = "EXPANDING" if total_change > 0 else "SHRINKING" if total_change < 0 else "STABLE"
            else:
                total_change = avg_change = 0
                trend = "UNKNOWN"
        else:
            total_change = avg_change = 0
            trend = "INSUFFICIENT_DATA"
        
        return {
            "success": True,
            "image_count": len(results),
            "individual_results": results,
            "trend_analysis": {
                "trend": trend,
                "total_lake_change_m2": round(total_change, 2),
                "average_change_per_image_m2": round(avg_change, 2)
            }
        }


# Global instance
_analyzer = None


def get_analyzer() -> LakeAnalyzer:
    """Get or create global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = LakeAnalyzer()
    return _analyzer
