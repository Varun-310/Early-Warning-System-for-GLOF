"""
SAR Image Analysis Service.
Handles GLOF detection from SAR satellite images using CNN model.
"""
import os
import numpy as np
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import settings


class SARAnalyzer:
    """Analyzes SAR images for GLOF detection using CNN model."""
    
    def __init__(self, model_path: str = None):
        """
        Initialize the analyzer with trained CNN model.
        
        Args:
            model_path: Path to the .h5 model file
        """
        self.model = None
        self.model_path = model_path or settings.MODEL_PATH
        self._load_model()
        
        # Import preprocessor
        from preprocessing_service import SARPreprocessor
        self.preprocessor = SARPreprocessor(target_size=(settings.IMAGE_SIZE, settings.IMAGE_SIZE))
    
    def _load_model(self):
        """Load the trained CNN model."""
        try:
            from tensorflow.keras.models import load_model
            
            model_path = Path(self.model_path)
            if not model_path.is_absolute():
                model_path = settings.BASE_DIR / model_path
            
            if model_path.exists():
                self.model = load_model(str(model_path))
                print(f"Model loaded successfully from {model_path}")
            else:
                print(f"Warning: Model not found at {model_path}")
                self.model = None
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Predict GLOF status from SAR image file.
        
        Args:
            image_path: Path to SAR image
            
        Returns:
            Dictionary with prediction results
        """
        if self.model is None:
            return {"error": "Model not loaded", "success": False}
        
        try:
            # Preprocess image
            processed_image = self.preprocessor.preprocess(image_path)
            
            # Get predictions
            predictions = self.model.predict(processed_image, verbose=0)[0]
            
            return self._format_prediction(predictions)
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def predict_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predict GLOF status from image bytes (for file upload).
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with prediction results
        """
        if self.model is None:
            return {"error": "Model not loaded", "success": False}
        
        try:
            # Preprocess image from bytes
            processed_image = self.preprocessor.preprocess_from_bytes(image_bytes)
            
            # Get predictions
            predictions = self.model.predict(processed_image, verbose=0)[0]
            
            return self._format_prediction(predictions)
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _format_prediction(self, predictions: np.ndarray) -> Dict[str, Any]:
        """
        Format raw model predictions into structured response.
        
        Args:
            predictions: Raw model output probabilities
            
        Returns:
            Formatted prediction dictionary
        """
        # Get class probabilities
        probabilities = {
            settings.CLASS_LABELS[i]: float(predictions[i]) * 100
            for i in range(len(predictions))
        }
        
        # Get predicted class
        predicted_class_idx = int(np.argmax(predictions))
        predicted_class = settings.CLASS_LABELS[predicted_class_idx]
        confidence = float(predictions[predicted_class_idx]) * 100
        
        # Get risk assessment
        risk_info = settings.RISK_MAPPING[predicted_class]
        
        # Calculate overall GLOF probability
        # Weight: during_glof has highest weight, pre_glof and post_glof contribute less
        glof_probability = (
            probabilities.get("during_glof", 0) * 1.0 +  # Full weight for active GLOF
            probabilities.get("post_glof", 0) * 0.3 +     # Partial weight for post-GLOF
            probabilities.get("pre_glof", 0) * 0.1        # Minimal weight for pre-GLOF
        )
        glof_probability = min(100, glof_probability)
        
        return {
            "success": True,
            "predicted_class": predicted_class,
            "confidence": round(confidence, 2),
            "probabilities": {k: round(v, 2) for k, v in probabilities.items()},
            "glof_probability": round(glof_probability, 2),
            "risk_level": risk_info["risk_level"],
            "risk_score": risk_info["risk_score"],
            "message": risk_info["message"]
        }
    
    def send_to_firebase(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send prediction results to Firebase.
        
        Args:
            prediction: Prediction dictionary
            
        Returns:
            Status of Firebase update
        """
        if not settings.FIREBASE_API_KEY or not settings.FIREBASE_DATABASE_URL:
            return {"success": False, "error": "Firebase not configured"}
        
        try:
            url = f"{settings.FIREBASE_DATABASE_URL}/GLOF_Predictions/prediction.json?auth={settings.FIREBASE_API_KEY}"
            
            data = {
                "value": int(prediction.get("glof_probability", 0)),
                "class": prediction.get("predicted_class", "unknown"),
                "risk_level": prediction.get("risk_level", "UNKNOWN"),
                "confidence": prediction.get("confidence", 0),
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
            
            response = requests.put(url, data=json.dumps(data))
            
            if response.status_code == 200:
                return {"success": True, "message": "Prediction sent to Firebase"}
            else:
                return {"success": False, "error": f"Firebase error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_batch(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple SAR images and aggregate results.
        
        Args:
            image_paths: List of paths to SAR images
            
        Returns:
            Aggregated analysis results
        """
        results = []
        
        for path in image_paths:
            result = self.predict(path)
            result["image_path"] = path
            results.append(result)
        
        # Calculate aggregate statistics
        successful = [r for r in results if r.get("success", False)]
        
        if successful:
            avg_probability = sum(r["glof_probability"] for r in successful) / len(successful)
            max_probability = max(r["glof_probability"] for r in successful)
            
            return {
                "success": True,
                "total_images": len(image_paths),
                "successful_analyses": len(successful),
                "average_glof_probability": round(avg_probability, 2),
                "max_glof_probability": round(max_probability, 2),
                "individual_results": results
            }
        else:
            return {
                "success": False,
                "error": "No images could be analyzed",
                "individual_results": results
            }


# Global analyzer instance
_analyzer = None


def get_analyzer() -> SARAnalyzer:
    """Get or create the global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SARAnalyzer()
    return _analyzer
