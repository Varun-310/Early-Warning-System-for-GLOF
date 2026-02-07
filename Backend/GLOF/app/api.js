import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export const getSensorData = async () => {
  const response = await axios.get(`${API_BASE_URL}/sensor-data`);
  return response.data;
};

export const sendAlert = async (phoneNumber, currentCoordinates) => {
  const response = await axios.post(`${API_BASE_URL}/send-alert`, {
    phone_number: phoneNumber,
    current_coordinates: currentCoordinates,
  });
  return response.data;
};
