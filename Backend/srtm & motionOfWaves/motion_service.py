"""
Motion Detection Service.
Detects water flow motion in video streams for GLOF monitoring.
"""
import io
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, Any, Union, List, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import settings


class MotionDetector:
    """Detects water flow motion in video streams."""
    
    def __init__(self):
        """Initialize motion detector with optical flow parameters."""
        self.optical_flow_params = {
            'pyr_scale': 0.5,
            'levels': 3,
            'winsize': 15,
            'iterations': 3,
            'poly_n': 5,
            'poly_sigma': 1.2,
            'flags': 0
        }
        
        self.pixel_to_meter = settings.PIXEL_TO_METER_CONVERSION
        self.estimated_depth = settings.ESTIMATED_DEPTH
        self.motion_threshold = settings.MOTION_THRESHOLD
    
    def analyze_frame_pair(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray
    ) -> Dict[str, Any]:
        """
        Analyze motion between two frames.
        
        Args:
            frame1: First frame (BGR)
            frame2: Second frame (BGR)
            
        Returns:
            Motion analysis results
        """
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        
        # Convert to HSV for water detection
        hsv = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
        
        # Create water mask
        water_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in settings.GLACIAL_LAKE_COLORS:
            lower = np.array(lower)
            upper = np.array(upper)
            mask = cv2.inRange(hsv, lower, upper)
            water_mask = cv2.bitwise_or(water_mask, mask)
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(
            gray1, gray2, None,
            **self.optical_flow_params
        )
        
        # Calculate magnitude
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        
        # Filter by motion threshold
        motion_mask = magnitude > self.motion_threshold
        combined_mask = cv2.bitwise_and(water_mask, motion_mask.astype(np.uint8) * 255)
        
        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate volumes
        total_volume = 0.0
        regions = []
        
        for contour in contours:
            pixel_area = cv2.contourArea(contour)
            if pixel_area > 100:
                real_area = pixel_area * (self.pixel_to_meter ** 2)
                volume = real_area * self.estimated_depth
                total_volume += volume
                
                x, y, w, h = cv2.boundingRect(contour)
                regions.append({
                    "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "area_m2": round(real_area, 4),
                    "volume_m3": round(volume, 4)
                })
        
        # Calculate average flow velocity
        avg_velocity = float(np.mean(magnitude[motion_mask])) if np.any(motion_mask) else 0
        
        return {
            "success": True,
            "water_detected_pixels": int(np.sum(water_mask > 0)),
            "motion_detected_pixels": int(np.sum(motion_mask)),
            "water_motion_regions": len(regions),
            "total_flow_volume_m3": round(total_volume, 4),
            "avg_flow_velocity": round(avg_velocity, 4),
            "regions": regions
        }
    
    def analyze_video(
        self,
        video_path: Union[str, Path],
        max_frames: int = 100,
        frame_skip: int = 1
    ) -> Dict[str, Any]:
        """
        Analyze video for water flow motion.
        
        Args:
            video_path: Path to video file
            max_frames: Maximum frames to analyze
            frame_skip: Process every Nth frame
            
        Returns:
            Aggregated motion analysis results
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            return {"success": False, "error": "Could not open video"}
        
        # Get video info
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        results = []
        prev_frame = None
        frame_count = 0
        analyzed_count = 0
        
        while cap.isOpened() and analyzed_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            if frame_count % frame_skip != 0:
                continue
            
            if prev_frame is not None:
                result = self.analyze_frame_pair(prev_frame, frame)
                result["frame_number"] = frame_count
                results.append(result)
                analyzed_count += 1
            
            prev_frame = frame.copy()
        
        cap.release()
        
        # Aggregate results
        if results:
            total_volumes = [r["total_flow_volume_m3"] for r in results]
            velocities = [r["avg_flow_velocity"] for r in results]
            
            avg_volume = sum(total_volumes) / len(total_volumes)
            max_volume = max(total_volumes)
            avg_velocity = sum(velocities) / len(velocities)
            
            risk_level, risk_message = self._assess_risk(avg_volume, avg_velocity)
        else:
            avg_volume = max_volume = avg_velocity = 0
            risk_level = "UNKNOWN"
            risk_message = "No frames analyzed"
        
        return {
            "success": True,
            "video_info": {
                "fps": fps,
                "total_frames": total_frames,
                "width": width,
                "height": height
            },
            "analysis": {
                "frames_analyzed": analyzed_count,
                "avg_flow_volume_m3": round(avg_volume, 4),
                "max_flow_volume_m3": round(max_volume, 4),
                "avg_flow_velocity": round(avg_velocity, 4)
            },
            "risk": {
                "level": risk_level,
                "message": risk_message
            }
        }
    
    def _assess_risk(self, avg_volume: float, avg_velocity: float) -> Tuple[str, str]:
        """Assess risk from motion metrics."""
        if avg_volume > 10 or avg_velocity > 5:
            return "HIGH", "Significant water motion detected - High flood risk"
        elif avg_volume > 5 or avg_velocity > 2:
            return "MODERATE", "Notable water motion - Monitor closely"
        else:
            return "LOW", "Normal water motion levels"
    
    def analyze_image_pair(
        self,
        image1_bytes: bytes,
        image2_bytes: bytes
    ) -> Dict[str, Any]:
        """
        Analyze motion between two uploaded images.
        
        Args:
            image1_bytes: First image bytes
            image2_bytes: Second image bytes
            
        Returns:
            Motion analysis results
        """
        # Decode images
        nparr1 = np.frombuffer(image1_bytes, np.uint8)
        nparr2 = np.frombuffer(image2_bytes, np.uint8)
        
        frame1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        frame2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)
        
        if frame1 is None or frame2 is None:
            return {"success": False, "error": "Could not decode images"}
        
        return self.analyze_frame_pair(frame1, frame2)


# Global instance
_motion_detector = None


def get_motion_detector() -> MotionDetector:
    """Get or create global motion detector instance."""
    global _motion_detector
    if _motion_detector is None:
        _motion_detector = MotionDetector()
    return _motion_detector
