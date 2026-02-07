import streamlit as st
import matplotlib.pyplot as plt
import time
import os
from prediction import generate_sensor_values, predict_glof_probability
from twilio.rest import Client
import geopy.distance
import serial
from fastapi import FastAPI

# Set up Matplotlib style for a black-themed graph
plt.style.use('dark_background')
app = FastAPI()
# Twilio setup
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = "+12766226657"      # Replace with your Twilio phone number
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# Sample list of safe locations (latitude, longitude, and name)
# Initialize RF module serial connection
# Initialize the serial communication
safe_locations = [
    {"name": "Gaurikund", "coordinates": (30.6603, 79.0327)},
    {"name": "Sonprayag", "coordinates": (30.61171, 78.97866)},
    {"name": "Rudraprayag", "coordinates": (30.284414, 78.981140)},
]

# Function to find the nearest safe location
def find_nearest_safe_location(current_coordinates):
    min_distance = float('inf')
    nearest_location = None

    for location in safe_locations:
        distance = geopy.distance.geodesic(current_coordinates, location["coordinates"]).km
        if distance < min_distance:
            min_distance = distance
            nearest_location = location

    return nearest_location

# Function to send SMS via Twilio
def send_sms(phone_number, message, current_coordinates):
    try:
        # Find the nearest safe location
        nearest_location = find_nearest_safe_location(current_coordinates)
        if nearest_location:
            safe_location_name = nearest_location["name"]
            safe_coordinates = nearest_location["coordinates"]
            safe_map_link = generate_map_link(safe_coordinates)
            location_message = (
                f"\nNearest Safe Location: {safe_location_name}\n"
                f"Coordinates: {safe_coordinates}\n"
                f"Map: {safe_map_link}"
            )
        else:
            location_message = "\nNo safe location data available."

        # Current location map link
        current_map_link = generate_map_link(current_coordinates)

        # Combine the messages
        full_message = (
            f"{message}\nRisk Location: {current_coordinates}\n"
            f"View on Map: {current_map_link}{location_message}"
        )

        # Send SMS
        for number in phone_number:
            sms = client.messages.create(
            body=full_message,
            from_='+12766226657',  # Replace with your Twilio phone number
            to=number
            )
        print("Message sent successfully:", sms.sid)
    except Exception as e:
        print("Error sending message:", e)
def generate_map_link(coordinates):
    latitude, longitude = coordinates
    return f"https://www.google.com/maps?q={latitude},{longitude}"



def main():
    st.set_page_config(layout="wide")  # Use the full screen
    st.title("Dynamic GLOF Probability and Parameter Dashboard")
    st.markdown("---")

    # Layout: Full-width graph for GLOF probability on top, parameter graphs below
    glof_col = st.container()
    param_cols = st.columns(4)  # Four columns for the parameter graphs

    # Placeholders for graphs
    glof_graph_placeholder = glof_col.empty()
    snowfall_graph_placeholder = param_cols[0].empty()
    rainfall_graph_placeholder = param_cols[1].empty()
    lake_size_graph_placeholder = param_cols[2].empty()
    water_level_graph_placeholder = param_cols[3].empty()

    # Fixed section for alerts and contributing sensors
    st.markdown("---")
    alert_col, sensor_col = st.columns([2, 3])
    alert_placeholder = alert_col.empty()
    sensor_placeholder = sensor_col.empty()

    # Initialize probabilities and parameter history
    probabilities = []
    snowfall_history = []
    rainfall_history = []
    lake_size_history = []
    water_level_history = []

    # Infinite loop for dynamic updates
    while True:
        # Generate new sensor values
        sensor_values = generate_sensor_values()

        # Predict GLOF probability and contributing sensors
        new_probability, contributing_sensors = predict_glof_probability(sensor_values)
        probabilities.append(new_probability)

        # Keep the last 20 values for plotting
        snowfall_history.append(sensor_values["Snowfall_mm"])
        rainfall_history.append(sensor_values["Rainfall_mm"])
        lake_size_history.append(sensor_values["Lake_Size_km2"])
        water_level_history.append(sensor_values["Water_Level_m"])

        # Trim history to last 20 points
        for history in [probabilities, snowfall_history, rainfall_history, lake_size_history, water_level_history]:
            if len(history) > 20:
                history.pop(0)

        # Update the GLOF Probability graph
        with glof_graph_placeholder.container():
            fig, ax = plt.subplots(figsize=(16, 8))  # Larger graph
            time_steps = range(len(probabilities))
            ax.plot(time_steps, probabilities, marker='o', linestyle='-', linewidth=2, color='cyan', label="GLOF Probability")
            ax.fill_between(time_steps, probabilities, color='cyan', alpha=0.3)
            ax.set_title("GLOF Probability Over Time", fontsize=20, color='white')
            ax.set_xlabel("Time Steps", fontsize=16, color='white')
            ax.set_ylabel("Probability", fontsize=16, color='white')
            ax.set_ylim(0, 1)
            ax.grid(visible=True, color='gray', linestyle='--', linewidth=0.5)
            ax.tick_params(colors='white')
            ax.legend(loc="upper left", fontsize=14, facecolor='black', edgecolor='white')
            st.pyplot(fig)

        # Update parameter graphs
        for placeholder, history, title, color in zip(
            [snowfall_graph_placeholder, rainfall_graph_placeholder, lake_size_graph_placeholder, water_level_graph_placeholder],
            [snowfall_history, rainfall_history, lake_size_history, water_level_history],
            ["Snowfall (mm)", "Rainfall (mm)", "Lake Size (km²)", "Water Level (m)"],
            ['blue', 'green', 'orange', 'red']
        ):
            with placeholder.container():
                fig, ax = plt.subplots(figsize=(6, 4))
                time_steps = range(len(history))
                ax.plot(time_steps, history, marker='o', linestyle='-', linewidth=2, color=color, label=title)
                ax.fill_between(time_steps, history, color=color, alpha=0.3)
                ax.set_title(title, fontsize=16, color='white')
                ax.set_xlabel("Time Steps", fontsize=12, color='white')
                ax.set_ylabel("Value", fontsize=12, color='white')
                ax.grid(visible=True, color='gray', linestyle='--', linewidth=0.5)
                ax.tick_params(colors='white')
                ax.legend(loc="upper left", fontsize=10, facecolor='black', edgecolor='white')
                st.pyplot(fig)

        # Update alert if probability is high
        if new_probability > 0.3:
         alert_placeholder.warning("⚠️ **High Risk Detected! Immediate action is recommended.**")
         current_location = (28.00333, 86.90749)  # Replace with actual coordinates of the risk location
         map_link = generate_map_link(current_location)  # Ensure map_link is defined

         # Display the map link in Streamlit
         st.markdown(f"🌍 **[View Risk Location on Map]({map_link})**")
         phone_numbers = [
           '+919944820144',  # Replace with the first recipient's phone number
           '+918668065755',
            '+919080901498',
            
          ]
         # Send the SMS alert
         send_sms(
          phone_numbers,  # Replace with the recipient's phone number
         f'⚠️ High Risk GLOF detected! Immediate action required. '
         f'Please evacuate to safety. View location: {map_link}',
         current_location
         )



         # Notify the user and provide restart options
         st.warning("⚠️ Alert sent! System will restart automatically in 5 minutes.")
         restart = st.button("Restart Now", key="restart_button")
         if restart:
           st.experimental_rerun()
         time.sleep(300)  # Wait for 5 minutes before restarting
         st.experimental_rerun()


        else:
            alert_placeholder.info("✅ Risk is under control.")

        # Update contributing sensors
        sensor_placeholder.markdown(f"**Top Contributing Parameters:**\n- {', '.join(contributing_sensors)}")

        # Pause for 2 seconds before updating
        time.sleep(2)

if __name__ == "__main__":
    main()
