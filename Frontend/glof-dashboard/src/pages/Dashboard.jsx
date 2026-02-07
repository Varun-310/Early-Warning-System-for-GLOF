import { useState, useEffect, useCallback } from 'react';
import {
    Droplets,
    Thermometer,
    Activity,
    Gauge,
    Mountain,
    CloudRain,
    TrendingUp,
    AlertTriangle,
    ArrowUpRight,
    X,
    Cloud,
    Wind,
    Droplet
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import Header from '../components/Header';
import api, { MOCK_DATA } from '../services/api';

export default function Dashboard() {
    const [prediction, setPrediction] = useState(null);
    const [sensors, setSensors] = useState(null);
    const [historicalData, setHistoricalData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedSensor, setSelectedSensor] = useState(null);
    const [sensorHistory, setSensorHistory] = useState([]);

    // Dynamic mock sensor values with smooth transitions
    const [liveSensors, setLiveSensors] = useState({
        lake_size_km2: 1.52,
        water_level_m: 10.5,
        temperature_c: 15.2,
        flow_rate_m3s: 102.5,
        ground_movement_mm: 2.1,
        dam_pressure_mpa: 1.05,
        precipitation_mm: 52.3
    });

    // Dynamic probability based on sensors
    const [livePrediction, setLivePrediction] = useState({
        probability: 32.5,
        risk_level: 'LOW',
        confidence: 87.5
    });

    const [weather, setWeather] = useState({
        temperature: 12,
        condition: 'Partly Cloudy',
        humidity: 68,
        windSpeed: 15
    });

    // Simulate realistic risk scenario changes
    const [riskScenario, setRiskScenario] = useState('normal'); // 'low', 'normal', 'high'

    // Calculate GLOF probability from sensor values
    const calculateProbability = useCallback((sensors) => {
        // Normalize each factor (0-1 scale based on thresholds)
        const waterLevelFactor = Math.min(sensors.water_level_m / 15, 1);
        const flowRateFactor = Math.min(sensors.flow_rate_m3s / 150, 1);
        const groundMovementFactor = Math.min(sensors.ground_movement_mm / 5, 1);
        const precipitationFactor = Math.min(sensors.precipitation_mm / 80, 1);
        const lakeSizeFactor = Math.min(sensors.lake_size_km2 / 2, 1);
        const pressureFactor = Math.min(sensors.dam_pressure_mpa / 1.5, 1);

        // Weighted combination
        const probability = (
            waterLevelFactor * 25 +
            flowRateFactor * 20 +
            groundMovementFactor * 20 +
            precipitationFactor * 15 +
            lakeSizeFactor * 10 +
            pressureFactor * 10
        );

        // Determine risk level
        let risk_level = 'LOW';
        if (probability >= 70) risk_level = 'HIGH';
        else if (probability >= 40) risk_level = 'MODERATE';

        return {
            probability: Math.min(100, Math.max(0, probability)),
            risk_level,
            confidence: 85 + Math.random() * 10
        };
    }, []);

    // Smooth value update with scenario-based variance
    const updateValue = useCallback((current, base, variance, scenario) => {
        let targetBase = base;
        let targetVariance = variance;

        // Adjust based on scenario
        if (scenario === 'high') {
            targetBase = base * 1.5; // Higher baseline for dangerous conditions
            targetVariance = variance * 2;
        } else if (scenario === 'low') {
            targetBase = base * 0.5; // Lower baseline for safe conditions
            targetVariance = variance * 0.5;
        }

        const change = (Math.random() - 0.5) * targetVariance;
        const newValue = current + (targetBase - current) * 0.1 + change; // Drift towards target
        const min = targetBase * 0.6;
        const max = targetBase * 1.4;
        return Math.max(min, Math.min(max, newValue));
    }, []);

    // Randomly change risk scenario every 10-20 seconds
    useEffect(() => {
        const scenarioInterval = setInterval(() => {
            const rand = Math.random();
            if (rand < 0.3) setRiskScenario('low');
            else if (rand < 0.7) setRiskScenario('normal');
            else setRiskScenario('high');
        }, 10000 + Math.random() * 10000);

        return () => clearInterval(scenarioInterval);
    }, []);

    // Update sensor values every 2 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            setLiveSensors(prev => {
                const newSensors = {
                    lake_size_km2: updateValue(prev.lake_size_km2, 1.52, 0.05, riskScenario),
                    water_level_m: updateValue(prev.water_level_m, 10.5, 0.5, riskScenario),
                    temperature_c: updateValue(prev.temperature_c, 15.2, 0.5, riskScenario),
                    flow_rate_m3s: updateValue(prev.flow_rate_m3s, 102.5, 10, riskScenario),
                    ground_movement_mm: updateValue(prev.ground_movement_mm, 2.1, 0.3, riskScenario),
                    dam_pressure_mpa: updateValue(prev.dam_pressure_mpa, 1.05, 0.05, riskScenario),
                    precipitation_mm: updateValue(prev.precipitation_mm, 52.3, 5, riskScenario)
                };

                // Update prediction based on new sensor values
                setLivePrediction(calculateProbability(newSensors));

                return newSensors;
            });

            // Also update weather slightly
            setWeather(prev => ({
                ...prev,
                temperature: Math.round(updateValue(prev.temperature, 12, 1, riskScenario)),
                humidity: Math.round(updateValue(prev.humidity, 68, 5, riskScenario)),
                windSpeed: Math.round(updateValue(prev.windSpeed, 15, 3, riskScenario))

            }));
        }, 2000);

        return () => clearInterval(interval);
    }, [updateValue, calculateProbability, riskScenario]);



    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        const [predData, sensorData, histData] = await Promise.all([
            api.getPrediction(),
            api.getSensors(),
            api.getHistoricalData()
        ]);
        setPrediction(predData);
        setSensors(sensorData);
        setHistoricalData(histData);
        setLoading(false);
    };

    const handleSensorClick = (sensor) => {
        const baseValue = sensor.value || 10;
        const history = Array.from({ length: 24 }, (_, i) => ({
            time: `${i}:00`,
            value: Math.max(0, baseValue + (Math.random() - 0.5) * baseValue * 0.4)
        }));
        setSensorHistory(history);
        setSelectedSensor(sensor);
    };

    const getRiskColor = (level) => {
        const colors = {
            'LOW': 'var(--color-success)',
            'MODERATE': 'var(--color-warning)',
            'HIGH': 'var(--color-danger)',
            'CRITICAL': '#991b1b'
        };
        return colors[level] || 'var(--color-info)';
    };

    const getRiskBadgeClass = (level) => {
        return `risk-badge ${level?.toLowerCase() || 'low'}`;
    };

    if (loading) {
        return (
            <>
                <Header title="Dashboard" />
                <div className="page-content">
                    <div className="loading"><div className="spinner"></div></div>
                </div>
            </>
        );
    }

    // Use live sensor values
    const sensorItems = [
        { label: 'Lake Size', value: liveSensors.lake_size_km2, unit: 'km²', icon: Droplets, color: '#3b82f6' },
        { label: 'Water Level', value: liveSensors.water_level_m, unit: 'm', icon: Activity, color: '#06b6d4' },
        { label: 'Temperature', value: liveSensors.temperature_c, unit: '°C', icon: Thermometer, color: '#ef4444' },
        { label: 'Flow Rate', value: liveSensors.flow_rate_m3s, unit: 'm³/s', icon: TrendingUp, color: '#10b981' },
        { label: 'Ground Movement', value: liveSensors.ground_movement_mm, unit: 'mm', icon: Mountain, color: '#f59e0b' },
        { label: 'Dam Pressure', value: liveSensors.dam_pressure_mpa, unit: 'MPa', icon: Gauge, color: '#8b5cf6' },
        { label: 'Precipitation', value: liveSensors.precipitation_mm, unit: 'mm', icon: CloudRain, color: '#6366f1' },
    ];

    const getStats = () => {
        if (sensorHistory.length === 0) return { min: 0, avg: 0, max: 0 };
        const values = sensorHistory.map(h => h.value);
        return {
            min: Math.min(...values),
            avg: values.reduce((a, b) => a + b, 0) / values.length,
            max: Math.max(...values)
        };
    };

    const stats = getStats();

    return (
        <>
            <Header title="Dashboard" />
            <div className="page-content">
                {prediction?.mock && (
                    <div className="alert-banner info">
                        <AlertTriangle size={18} />
                        <span>Displaying simulated data. Values update every 2 seconds.</span>
                    </div>
                )}

                {/* Risk Overview */}
                <div className="grid grid-3" style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <div className="card" style={{
                        background: `linear-gradient(135deg, ${getRiskColor(livePrediction.risk_level)}15, ${getRiskColor(livePrediction.risk_level)}05)`,
                        borderColor: getRiskColor(livePrediction.risk_level),
                        transition: 'all 0.5s ease'
                    }}>
                        <div className="card-header">
                            <span className="card-title">GLOF Probability</span>
                            <span className={getRiskBadgeClass(livePrediction.risk_level)} style={{ transition: 'all 0.3s ease' }}>
                                {livePrediction.risk_level}
                            </span>
                        </div>
                        <div style={{
                            fontSize: '3rem',
                            fontWeight: '700',
                            color: getRiskColor(livePrediction.risk_level),
                            marginBottom: 'var(--spacing-sm)',
                            transition: 'all 0.3s ease'
                        }}>
                            {livePrediction.probability.toFixed(1)}%
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            Confidence: {livePrediction.confidence.toFixed(1)}%
                        </div>
                    </div>


                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">Sensor Accuracy</span>
                        </div>
                        <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--color-success)' }}>
                            {sensors?.sensor_accuracy?.toFixed(1) || 95}%
                        </div>
                        <div className="stat-card-change positive" style={{ marginTop: 'var(--spacing-sm)' }}>
                            <ArrowUpRight size={14} />
                            <span>All sensors operational</span>
                        </div>
                    </div>

                    {/* Weather */}
                    <div className="card" style={{ background: 'linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%)' }}>
                        <div className="card-header">
                            <span className="card-title">Weather</span>
                            <span style={{ fontSize: '0.75rem', color: '#0369a1' }}>Sikkim</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                            <Cloud size={32} style={{ color: '#0284c7' }} />
                            <div>
                                <div style={{ fontSize: '2rem', fontWeight: '700', color: '#0369a1', transition: 'all 0.3s ease' }}>
                                    {weather.temperature}°C
                                </div>
                                <div style={{ fontSize: '0.75rem', color: '#0369a1' }}>{weather.condition}</div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: 'var(--spacing-lg)', fontSize: '0.75rem', color: '#0369a1', marginTop: 'var(--spacing-sm)' }}>
                            <span><Droplet size={12} /> {weather.humidity}%</span>
                            <span><Wind size={12} /> {weather.windSpeed} km/h</span>
                        </div>
                    </div>
                </div>

                {/* Chart */}
                <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <div className="card-header">
                        <span className="card-title">GLOF Probability Trend (24h)</span>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={historicalData}>
                                <defs>
                                    <linearGradient id="colorProbability" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                                <XAxis dataKey="time" stroke="var(--text-tertiary)" fontSize={12} />
                                <YAxis stroke="var(--text-tertiary)" fontSize={12} domain={[0, 100]} />
                                <Tooltip
                                    contentStyle={{
                                        background: 'var(--bg-primary)',
                                        border: '1px solid var(--border-color)',
                                        borderRadius: 'var(--border-radius-sm)'
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="probability"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorProbability)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Sensor Grid */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Live Sensor Data</span>
                        <span className="card-subtitle">
                            <span style={{
                                display: 'inline-block',
                                width: '8px',
                                height: '8px',
                                background: '#10b981',
                                borderRadius: '50%',
                                marginRight: '6px',
                                animation: 'pulse 2s infinite'
                            }}></span>
                            Real-time updates
                        </span>
                    </div>
                    <div className="sensor-grid">
                        {sensorItems.map((sensor, index) => (
                            <div
                                key={index}
                                className="sensor-item"
                                onClick={() => handleSensorClick(sensor)}
                                style={{ cursor: 'pointer', transition: 'all 0.2s ease' }}
                                onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                                onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-sm)' }}>
                                    <div style={{
                                        width: '32px',
                                        height: '32px',
                                        borderRadius: 'var(--border-radius-sm)',
                                        background: `${sensor.color}15`,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}>
                                        <sensor.icon size={16} style={{ color: sensor.color }} />
                                    </div>
                                    <span className="sensor-label">{sensor.label}</span>
                                </div>
                                <div style={{ transition: 'all 0.3s ease' }}>
                                    <span className="sensor-value">{sensor.value?.toFixed(2)}</span>
                                    <span className="sensor-unit">{sensor.unit}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Sensor Detail Modal */}
            {selectedSensor && (
                <div className="modal-overlay" style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }} onClick={() => setSelectedSensor(null)}>
                    <div className="modal-content" style={{
                        background: 'var(--bg-primary)',
                        borderRadius: 'var(--border-radius-lg)',
                        padding: 'var(--spacing-lg)',
                        width: '600px',
                        boxShadow: 'var(--shadow-lg)'
                    }} onClick={(e) => e.stopPropagation()}>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    borderRadius: 'var(--border-radius)',
                                    background: `${selectedSensor.color}15`,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <selectedSensor.icon size={20} style={{ color: selectedSensor.color }} />
                                </div>
                                <div>
                                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>{selectedSensor.label}</h3>
                                    <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>24-hour data</p>
                                </div>
                            </div>
                            <button
                                onClick={() => setSelectedSensor(null)}
                                style={{
                                    background: 'var(--bg-secondary)',
                                    border: 'none',
                                    borderRadius: '50%',
                                    width: '32px',
                                    height: '32px',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}
                            >
                                <X size={18} />
                            </button>
                        </div>

                        <div style={{
                            background: `${selectedSensor.color}10`,
                            borderRadius: 'var(--border-radius)',
                            padding: 'var(--spacing-md)',
                            marginBottom: 'var(--spacing-md)',
                            textAlign: 'center'
                        }}>
                            <div style={{ fontSize: '2.5rem', fontWeight: '700', color: selectedSensor.color }}>
                                {selectedSensor.value?.toFixed(2)}
                                <span style={{ fontSize: '1.25rem', marginLeft: '6px' }}>{selectedSensor.unit}</span>
                            </div>
                        </div>

                        <div style={{ height: '180px', marginBottom: 'var(--spacing-md)' }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={sensorHistory}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                                    <XAxis dataKey="time" stroke="var(--text-tertiary)" fontSize={10} />
                                    <YAxis stroke="var(--text-tertiary)" fontSize={10} />
                                    <Tooltip
                                        contentStyle={{
                                            background: 'var(--bg-primary)',
                                            border: '1px solid var(--border-color)',
                                            borderRadius: 'var(--border-radius-sm)',
                                            fontSize: '0.875rem'
                                        }}
                                        formatter={(value) => [`${value.toFixed(2)} ${selectedSensor.unit}`, selectedSensor.label]}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="value"
                                        stroke={selectedSensor.color}
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--spacing-sm)' }}>
                            <div style={{ textAlign: 'center', padding: 'var(--spacing-sm)', background: 'var(--bg-secondary)', borderRadius: 'var(--border-radius-sm)' }}>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Min</div>
                                <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{stats.min.toFixed(2)} {selectedSensor.unit}</div>
                            </div>
                            <div style={{ textAlign: 'center', padding: 'var(--spacing-sm)', background: 'var(--bg-secondary)', borderRadius: 'var(--border-radius-sm)' }}>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Avg</div>
                                <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{stats.avg.toFixed(2)} {selectedSensor.unit}</div>
                            </div>
                            <div style={{ textAlign: 'center', padding: 'var(--spacing-sm)', background: 'var(--bg-secondary)', borderRadius: 'var(--border-radius-sm)' }}>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>Max</div>
                                <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{stats.max.toFixed(2)} {selectedSensor.unit}</div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <style>{`
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            `}</style>
        </>
    );
}
