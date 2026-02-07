# 🏔️ GLOF Early Warning System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive **Glacial Lake Outburst Flood (GLOF)** prediction and early warning system developed for Smart India Hackathon 2024 (SIH1650).

![Dashboard Preview](docs/dashboard-preview.png)

## 🌟 Features

- **Real-time GLOF Probability** - XGBoost-based prediction with live sensor data
- **Interactive Dashboard** - Beautiful React UI with dynamic visualizations
- **SAR Image Analysis** - Sentinel-1 SAR image classification using CNN
- **Lake Size Detection** - Automated glacial lake boundary detection
- **Terrain Analysis** - DEM-based water flow and motion detection
- **SMS Alerts** - Emergency notifications via Twilio
- **Weather Integration** - Live weather data display

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Git

### One-Click Start (Windows)

```bash
start.bat
```

### Manual Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Varun-310/Early-Warning-System-for-GLOF.git
cd Early-Warning-System-for-GLOF
```

#### 2. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Install Frontend Dependencies
```bash
cd Frontend/glof-dashboard
npm install
cd ../..
```

#### 4. Start the Application
```bash
python run.py
```

Or start services individually:
```bash
python run.py --backend     # Backend gateway only
python run.py --frontend    # Frontend only
python run.py --all-services # All microservices
```

## 📁 Project Structure

```
├── Backend/
│   ├── gateway/              # API Gateway (Port 8000)
│   ├── GLOF/                 # GLOF Prediction Service (Port 8001)
│   │   ├── main.py           # FastAPI endpoints
│   │   ├── prediction_service.py # XGBoost prediction logic
│   │   └── models/           # Trained ML models
│   ├── SAR/                  # SAR Analysis Service (Port 8002)
│   ├── lake_size/            # Lake Analysis Service (Port 8003)
│   └── srtm & motionOfWaves/ # Terrain Service (Port 8004)
│
├── Frontend/
│   └── glof-dashboard/       # React + Vite Dashboard
│       ├── src/
│       │   ├── pages/        # Page components
│       │   ├── components/   # Reusable components
│       │   └── services/     # API service layer
│       └── package.json
│
├── Hardware/
│   └── THE_FINAL_RECEIVER/   # Arduino IoT sensor code
│
├── requirements.txt          # Python dependencies
├── run.py                    # Main runner script
└── start.bat                 # Windows quick launcher
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/glof/predict` | GET | Get GLOF probability prediction |
| `/api/glof/sensors` | GET | Get real-time sensor values |
| `/api/glof/history` | GET | Get historical prediction data |
| `/api/sar/analyze` | POST | Analyze SAR satellite image |
| `/api/lake/analyze` | POST | Analyze lake size from image |
| `/api/terrain/dem/analyze` | POST | Analyze DEM elevation data |
| `/api/terrain/motion/analyze` | POST | Analyze water motion from video |
| `/health` | GET | Service health check |

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **XGBoost** - GLOF prediction model
- **TensorFlow/Keras** - CNN for SAR classification
- **OpenCV** - Image processing
- **Rasterio** - GeoTIFF/DEM processing
- **Twilio** - SMS alert system

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Recharts** - Data visualization
- **Lucide React** - Icons

### Hardware
- **Arduino/ESP32** - IoT sensor nodes
- **LoRa** - Long-range communication

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in `Backend/GLOF/`:

```env
# Firebase Configuration
FIREBASE_URL=https://your-project.firebaseio.com
FIREBASE_API_KEY=your-api-key

# Twilio SMS Alerts
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890
ALERT_PHONE_NUMBERS=+91XXXXXXXXXX

# Sensor Thresholds
WATER_LEVEL_THRESHOLD=15.0
FLOW_RATE_THRESHOLD=150.0
```

## 🧪 Testing

```bash
# Run backend tests
cd Backend/GLOF
python -m pytest

# Run frontend tests
cd Frontend/glof-dashboard
npm test
```

## 📊 Model Training

The GLOF prediction model uses XGBoost trained on:
- Water level data
- Flow rate measurements
- Precipitation records
- Ground movement sensors
- Historical GLOF events

To retrain the model:
```bash
cd Backend/GLOF
python train_model.py
```

## 🚨 Alert System

The system sends SMS alerts when:
- GLOF probability exceeds 70% (HIGH risk)
- Rapid sensor value changes detected
- Communication with sensors is lost

## 📱 Hardware Integration

The system integrates with IoT sensors via LoRa:
- Water level sensors
- Temperature sensors
- Flow rate monitors
- Ground movement detectors

See `Hardware/` folder for Arduino code.

## 🤝 Team Slytherin

Developed by **Team Slytherin** for **Smart India Hackathon 2024** (Problem Statement: SIH1650)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Indian Space Research Organisation (ISRO)
- National Remote Sensing Centre (NRSC)
- Smart India Hackathon 2024 organizers

---

Made with ❤️ for a safer Himalayan region
