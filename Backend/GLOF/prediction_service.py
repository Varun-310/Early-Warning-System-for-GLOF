"""
GLOF Prediction Service.
Handles sensor data generation and GLOF probability prediction.
"""
import os
import numpy as np
import pandas as pd
import xgboost as xgb
from pathlib import Path
from typing import Tuple, List, Dict, Any


class GLOFPredictor:
    """GLOF Prediction using XGBoost model."""
    
    def __init__(self, model_path: str = None):
        """Initialize the predictor with the trained model."""
        self.model = None
        self.model_loaded = False
        
        if model_path is None:
            # Use cross-platform path
            model_path = Path(__file__).parent / "models" / "glof_prediction_model.pkl"
        
        try:
            if os.path.exists(model_path):
                # Try loading as Booster first (more compatible)
                self.model = xgb.Booster()
                self.model.load_model(str(model_path))
                self.model_loaded = True
                print(f"Model loaded successfully from {model_path}")
        except Exception as e:
            print(f"Warning: Could not load model from {model_path}: {e}")
            print("Using mock predictions instead.")
            self.model_loaded = False
        
        # Sensor baseline values for simulation

        self.sensor_baseline = {
            "Lake_Size_km2": 1.5,
            "Water_Level_m": 10.0,
            "Air_Temperature_C": 15.0,
            "Flow_Rate_m3_per_s": 100.0,
            "Ground_Movement_mm": 2.0,
            "Dam_Pressure_MPa": 1.0,
            "Precipitation_mm": 50.0,
            "Sensor_Accuracy_%": 95.0,
            "Lake_Perimeter_Change_m": 5.0,
            "Snowpack_Thickness_m": 2.5,
            "Soil_Moisture_Content_%": 30.0,
            "Solar_Radiation_W_per_m2": 300.0,
            "Water_Temperature_C": 12.5,
            "Water_Turbidity_NTU": 5.0,
            "Wind_Speed_m_per_s": 10.0,
            "Rainfall_mm": 75.0,
            "Snowfall_mm": 25.0,
        }
    
    def generate_sensor_values(self) -> Dict[str, float]:
        """
        Generate simulated sensor values with gradual changes.
        
        Returns:
            Dictionary of sensor names to current values.
        """
        # Apply random changes (fixed the inverted range bug from original)
        for key in self.sensor_baseline:
            change = np.random.uniform(-0.5, 0.5)
            self.sensor_baseline[key] = max(0, self.sensor_baseline[key] + change)
        
        return self.sensor_baseline.copy()
    
    def predict(self, sensor_values: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Predict GLOF probability from sensor values.
        
        Args:
            sensor_values: Dictionary of sensor readings. If None, generates simulated values.
            
        Returns:
            Dictionary with probability, risk level, and top contributing factors.
        """
        if sensor_values is None:
            sensor_values = self.generate_sensor_values()
        
        probability = 0.0
        top_features = []
        
        if self.model_loaded and self.model is not None:
            try:
                # Create DMatrix for prediction
                input_df = pd.DataFrame([sensor_values])
                dmatrix = xgb.DMatrix(input_df)
                probability = float(self.model.predict(dmatrix)[0])
                
                # Get top contributing features
                feature_importance = self.model.get_score(importance_type='weight')
                sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
                top_features = [item[0] for item in sorted_features[:3]]
            except Exception as e:
                print(f"Prediction error: {e}")
                probability = self._generate_mock_probability(sensor_values)
                top_features = ["Water_Level_m", "Flow_Rate_m3_per_s", "Ground_Movement_mm"]
        else:
            # Generate realistic mock probability based on sensor values
            probability = self._generate_mock_probability(sensor_values)
            top_features = ["Water_Level_m", "Flow_Rate_m3_per_s", "Ground_Movement_mm"]
        
        # Determine risk level
        if probability >= 0.7:
            risk_level = "HIGH"
            risk_message = "High Risk of GLOF - Immediate action recommended"
        elif probability >= 0.4:
            risk_level = "MODERATE"
            risk_message = "Moderate Risk - Monitor closely"
        else:
            risk_level = "LOW"
            risk_message = "Low Risk - Normal conditions"
        
        return {
            "probability": round(probability * 100, 2),  # Return as percentage
            "risk_level": risk_level,
            "risk_message": risk_message,
            "top_contributing_factors": top_features,
            "sensor_values": sensor_values
        }
    
    def _generate_mock_probability(self, sensor_values: Dict[str, float]) -> float:
        """Generate a realistic mock probability based on sensor values."""
        # Weight factors that would indicate higher risk
        water_level = sensor_values.get("Water_Level_m", 10.0)
        flow_rate = sensor_values.get("Flow_Rate_m3_per_s", 100.0)
        ground_movement = sensor_values.get("Ground_Movement_mm", 2.0)
        precipitation = sensor_values.get("Precipitation_mm", 50.0)
        
        # Normalize and combine (simple heuristic)
        water_factor = min(water_level / 20.0, 1.0)
        flow_factor = min(flow_rate / 200.0, 1.0)
        movement_factor = min(ground_movement / 10.0, 1.0)
        precip_factor = min(precipitation / 100.0, 1.0)
        
        # Weighted average with some randomness
        base_prob = (water_factor * 0.3 + flow_factor * 0.25 + 
                     movement_factor * 0.25 + precip_factor * 0.2)
        noise = np.random.uniform(-0.05, 0.05)
        
        return max(0.0, min(1.0, base_prob + noise))


# Global predictor instance
_predictor = None


def get_predictor() -> GLOFPredictor:
    """Get or create the global predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = GLOFPredictor()
    return _predictor
