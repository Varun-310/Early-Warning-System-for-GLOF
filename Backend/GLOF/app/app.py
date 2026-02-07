import streamlit as st
import xgboost as xgb
import pandas as pd
import numpy as np
import time

# Load the trained model
def load_model():
    model = xgb.XGBClassifier()
    model.load_model('data/glof_prediction_model.pkl')  # Replace with your model path
    return model

# Simulate predictions and display sensor data
def simulate_continuous_predictions():
    st.set_page_config(layout="wide")  # Enable full landscape mode
    st.title("GLOF Prediction and Monitoring Dashboard")
    
    # Sidebar for flood risk alert
    with st.sidebar:
        st.header("Flood Risk Alert 🚨")
        alert_box = st.empty()
    
    # Section for Sensor Values
    st.subheader("Current Sensor Values")
    col1, col2, col3 = st.columns(3)  # Organize into 3 columns for neat display
    
    # Initialize placeholders for sensor metrics
    lake_size_box = col1.empty()
    water_level_box = col1.empty()
    air_temp_box = col1.empty()
    
    flow_rate_box = col2.empty()
    ground_movement_box = col2.empty()
    dam_pressure_box = col2.empty()
    
    precipitation_box = col3.empty()
    sensor_accuracy_box = col3.empty()

    # Flood probability graphs
    st.subheader("Flood Risk Over Time")
    probability_chart = st.line_chart([])

    st.subheader("Future Flood Risk Predictions")
    future_chart = st.line_chart([])

    # Load the model
    model = load_model()
    probabilities = []
    future_probabilities = []

    for _ in range(50000):  # Simulate 50 time steps
        # Randomly generate sensor input data with dynamic variations
        lake_size = np.random.uniform(50, 200)
        water_level = np.random.uniform(0, 50)
        air_temp = np.random.uniform(-20, 40)
        flow_rate = np.random.uniform(0, 10)
        ground_movement = np.random.uniform(0, 10)
        dam_pressure = np.random.uniform(0, 10)
        precipitation = np.random.uniform(0, 300)
        sensor_accuracy = np.random.uniform(90, 100)

        input_data = {
            'Lake_Size_km2': [lake_size],
            'Water_Level_m': [water_level],
            'Air_Temperature_C': [air_temp],
            'Flow_Rate_m3_per_s': [flow_rate],
            'Ground_Movement_mm': [ground_movement],
            'Dam_Pressure_MPa': [dam_pressure],
            'Precipitation_mm': [precipitation],
            'Sensor_Accuracy_%': [sensor_accuracy],
        }
        input_df = pd.DataFrame(input_data)

        # Predict flood risk probability
        probability = model.predict_proba(input_df)[0][1]  # Flood risk probability
        probability = max(0, min(1, probability + np.random.normal(0, 0.05)))

        # Append to graphs
        probabilities.append(probability)
        probability_chart.line_chart(probabilities)

        # Predict future flood risk probabilities (mock predictions)
        future_probability = max(0, min(1, probability + np.random.normal(0, 0.1)))
        future_probabilities.append(future_probability)
        future_chart.line_chart(future_probabilities)

        # Update alert box
        if probability > 0.7:  # Threshold for high flood risk
            alert_box.error(f"High Flood Risk Detected! 🚨 Probability: {probability:.2f}")
        else:
            alert_box.success(f"Flood Risk Under Control. Probability: {probability:.2f}")

        # Update sensor data boxes
        lake_size_box.metric("Lake Size (km²)", f"{lake_size:.2f}")
        water_level_box.metric("Water Level (m)", f"{water_level:.2f}")
        air_temp_box.metric("Air Temperature (°C)", f"{air_temp:.2f}")
        
        flow_rate_box.metric("Flow Rate (m³/s)", f"{flow_rate:.2f}")
        ground_movement_box.metric("Ground Movement (mm)", f"{ground_movement:.2f}")
        dam_pressure_box.metric("Dam Pressure (MPa)", f"{dam_pressure:.2f}")
        
        precipitation_box.metric("Precipitation (mm)", f"{precipitation:.2f}")
        sensor_accuracy_box.metric("Sensor Accuracy (%)", f"{sensor_accuracy:.2f}")

        # Simulate delay
        time.sleep(1)

# Run the Streamlit app
if __name__ == "__main__":
    simulate_continuous_predictions()
