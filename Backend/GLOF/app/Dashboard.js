import React, { useState, useEffect } from "react";
import { getSensorData, sendAlert } from "./api";

function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getSensorData();
        setData(result);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching sensor data:", error);
      }
    };
    fetchData();
  }, []);

  const handleSendAlert = async () => {
    try {
      const response = await sendAlert("+919080904107", [28.00333, 86.90749]);
      alert(response.status);
    } catch (error) {
      console.error("Error sending alert:", error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>GLOF Monitoring Dashboard</h1>
      <div>
        <h2>Probability: {data.probability}</h2>
        <p>Contributing Sensors: {data.contributing_sensors.join(", ")}</p>
        <button onClick={handleSendAlert}>Send Alert</button>
      </div>
    </div>
  );
}

export default Dashboard;
