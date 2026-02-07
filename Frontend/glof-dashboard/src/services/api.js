// API Service with Mock Data Fallback

const API_BASE = 'http://localhost:8000';

// Mock Data (used when API is unavailable)
export const MOCK_DATA = {
  prediction: {
    probability: 23.5,
    risk_level: 'MODERATE',
    confidence: 87.2,
    timestamp: new Date().toISOString(),
    mock: true
  },
  
  sensors: {
    lake_size_km2: 1.52,
    water_level_m: 10.3,
    temperature_c: 14.7,
    flow_rate_m3s: 105.2,
    ground_movement_mm: 2.1,
    dam_pressure_mpa: 1.02,
    precipitation_mm: 48.5,
    sensor_accuracy: 95.2,
    mock: true
  },
  
  sarAnalysis: {
    success: true,
    predicted_class: 'pre_glof',
    confidence: 78.5,
    probabilities: { pre_glof: 78.5, during_glof: 12.3, post_glof: 9.2 },
    glof_probability: 15.2,
    risk_level: 'LOW',
    message: 'Normal conditions - Pre-GLOF state',
    mock: true
  },
  
  lakeAnalysis: {
    success: true,
    lake: { size_before_m2: 15000, size_after_m2: 15200, change_percent: 1.3 },
    ice: { size_before_m2: 8000, size_after_m2: 7800, change_percent: -2.5, status: '7800 m²' },
    coverage: { total_area_m2: 50000, water_percentage: 30.4 },
    risk: { level: 'LOW', message: 'Lake conditions stable' },
    mock: true
  },
  
  demAnalysis: {
    success: true,
    elevation: { min_m: 3200, max_m: 4500, mean_m: 3850, water_level_threshold_m: 3400 },
    water_flow: { submerged_volume_m3: 25000, submerged_area_m2: 5000, overflow_rate_m3_per_s: 250, avg_flow_velocity_m_per_s: 0.25 },
    risk: { level: 'MODERATE', message: 'Moderate water flow - Monitor conditions' },
    mock: true
  },
  
  motionAnalysis: {
    success: true,
    video_info: { fps: 30, total_frames: 300, width: 1920, height: 1080 },
    analysis: { frames_analyzed: 50, avg_flow_volume_m3: 2.5, max_flow_volume_m3: 4.8, avg_flow_velocity: 1.2 },
    risk: { level: 'LOW', message: 'Normal water motion levels' },
    mock: true
  },
  
  // Historical data for charts
  historicalData: Array.from({ length: 24 }, (_, i) => ({
    time: `${i}:00`,
    probability: 15 + Math.random() * 20,
    waterLevel: 10 + Math.random() * 1.5,
    temperature: 12 + Math.random() * 5
  }))
};

// API Functions
async function fetchWithFallback(endpoint, fallbackData, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    if (!response.ok) throw new Error('API Error');
    return await response.json();
  } catch (error) {
    console.log(`API unavailable for ${endpoint}, using mock data`);
    return fallbackData;
  }
}

export const api = {
  // GLOF Prediction
  getPrediction: () => fetchWithFallback('/api/glof/predict', MOCK_DATA.prediction),
  getSensors: () => fetchWithFallback('/api/glof/sensors', MOCK_DATA.sensors),
  
  // SAR Analysis
  analyzeSAR: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE}/api/sar/analyze`, {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('API Error');
      return await response.json();
    } catch {
      return MOCK_DATA.sarAnalysis;
    }
  },
  
  // Lake Analysis
  analyzeLake: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE}/api/lake/analyze`, {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('API Error');
      return await response.json();
    } catch {
      return MOCK_DATA.lakeAnalysis;
    }
  },
  
  // DEM Analysis
  analyzeDEM: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE}/api/terrain/dem/analyze`, {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('API Error');
      return await response.json();
    } catch {
      return MOCK_DATA.demAnalysis;
    }
  },
  
  // Motion Analysis
  analyzeMotion: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE}/api/terrain/motion/analyze`, {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('API Error');
      return await response.json();
    } catch {
      return MOCK_DATA.motionAnalysis;
    }
  },
  
  // Get historical data
  getHistoricalData: () => Promise.resolve(MOCK_DATA.historicalData),
  
  // Service status
  getStatus: () => fetchWithFallback('/api/status', { mock: true, services: {} })
};

export default api;
