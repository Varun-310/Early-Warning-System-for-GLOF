import numpy as np
import pandas as pd
import xgboost as xgb


# Load the trained model
model = xgb.XGBClassifier()
model.load_model("models\glof_prediction_model.pkl")  # Ensure the model file path is correct
# Initialize baseline sensor values
sensor_baseline = {
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

# Function to gradually change sensor values
def generate_sensor_values():
    changes = {key: np.random.uniform(0.5, -0.1) for key in sensor_baseline.keys()}
    for key, change in changes.items():
        sensor_baseline[key] = max(0, sensor_baseline[key] + change)  # Ensure no negative values
    return sensor_baseline

# Function to predict GLOF probability and identify contributing sensors
def predict_glof_probability(sensor_values):
    input_df = pd.DataFrame([sensor_values])
    probability = model.predict_proba(input_df)[:, 1][0]  # Probability for class "1" (GLOF occurred)
    
    # Identify contributing sensors by feature importance
    feature_importance = model.get_booster().get_score(importance_type='weight')
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    top_features = [item[0] for item in sorted_features[:3]]  # Top 3 features
    return probability, top_features
