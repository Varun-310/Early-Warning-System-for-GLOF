import { useState, useRef } from 'react';
import { Mountain, Video, Upload, Activity, Gauge, AlertTriangle, X, FileImage } from 'lucide-react';
import Header from '../components/Header';
import api from '../services/api';

export default function TerrainAnalysis() {
    const [activeTab, setActiveTab] = useState('dem');
    const [file, setFile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setResult(null);
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;
        setLoading(true);
        const analysisResult = activeTab === 'dem'
            ? await api.analyzeDEM(file)
            : await api.analyzeMotion(file);
        setResult(analysisResult);
        setLoading(false);
    };

    const clearFile = () => {
        setFile(null);
        setResult(null);
    };

    return (
        <>
            <Header title="Terrain Analysis" />
            <div className="page-content">
                {/* Modern Toggle Tabs */}
                <div style={{
                    display: 'inline-flex',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '12px',
                    padding: '4px',
                    marginBottom: 'var(--spacing-lg)'
                }}>
                    <button
                        onClick={() => { setActiveTab('dem'); clearFile(); }}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '10px 20px',
                            borderRadius: '8px',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            transition: 'all 0.2s ease',
                            background: activeTab === 'dem' ? 'var(--bg-primary)' : 'transparent',
                            color: activeTab === 'dem' ? 'var(--color-primary)' : 'var(--text-secondary)',
                            boxShadow: activeTab === 'dem' ? 'var(--shadow-sm)' : 'none'
                        }}
                    >
                        <Mountain size={16} />
                        DEM Analysis
                    </button>
                    <button
                        onClick={() => { setActiveTab('motion'); clearFile(); }}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '10px 20px',
                            borderRadius: '8px',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            transition: 'all 0.2s ease',
                            background: activeTab === 'motion' ? 'var(--bg-primary)' : 'transparent',
                            color: activeTab === 'motion' ? 'var(--color-primary)' : 'var(--text-secondary)',
                            boxShadow: activeTab === 'motion' ? 'var(--shadow-sm)' : 'none'
                        }}
                    >
                        <Video size={16} />
                        Motion Detection
                    </button>
                </div>

                <div className="grid grid-2">
                    {/* Upload Section */}
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">
                                {activeTab === 'dem' ? 'Upload DEM File' : 'Upload Video'}
                            </span>
                        </div>

                        {!file ? (
                            <div
                                className="upload-zone"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                {activeTab === 'dem' ? (
                                    <Mountain size={48} className="upload-zone-icon" />
                                ) : (
                                    <Video size={48} className="upload-zone-icon" />
                                )}
                                <p className="upload-zone-text">
                                    <span>Click to upload</span> or drag and drop
                                </p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: 'var(--spacing-sm)' }}>
                                    {activeTab === 'dem' ? 'GeoTIFF DEM files (.tif)' : 'Video files (MP4, AVI)'}
                                </p>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept={activeTab === 'dem' ? '.tif,.tiff' : '.mp4,.avi,.mov'}
                                    onChange={handleFileSelect}
                                    style={{ display: 'none' }}
                                />
                            </div>
                        ) : (
                            <div>
                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-sm)',
                                    padding: 'var(--spacing-md)',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: 'var(--border-radius)',
                                    marginBottom: 'var(--spacing-md)'
                                }}>
                                    <FileImage size={24} style={{ color: 'var(--text-tertiary)' }} />
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: '500' }}>{file.name}</div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                                            {(file.size / 1024 / 1024).toFixed(2)} MB
                                        </div>
                                    </div>
                                    <button
                                        onClick={clearFile}
                                        style={{
                                            background: 'none',
                                            border: 'none',
                                            cursor: 'pointer',
                                            color: 'var(--text-tertiary)'
                                        }}
                                    >
                                        <X size={18} />
                                    </button>
                                </div>

                                <button
                                    className="btn btn-primary"
                                    onClick={handleAnalyze}
                                    disabled={loading}
                                    style={{ width: '100%' }}
                                >
                                    {loading ? 'Analyzing...' : 'Analyze'}
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Results Section */}
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">Analysis Results</span>
                        </div>

                        {!result ? (
                            <div className="empty-state">
                                {activeTab === 'dem' ? (
                                    <Mountain size={48} style={{ color: 'var(--text-tertiary)', marginBottom: 'var(--spacing-md)' }} />
                                ) : (
                                    <Video size={48} style={{ color: 'var(--text-tertiary)', marginBottom: 'var(--spacing-md)' }} />
                                )}
                                <p>Upload a file to see analysis results</p>
                            </div>
                        ) : (
                            <div>
                                {result.mock && (
                                    <div className="alert-banner info" style={{ marginBottom: 'var(--spacing-md)' }}>
                                        <AlertTriangle size={16} />
                                        <span style={{ fontSize: '0.875rem' }}>Mock data</span>
                                    </div>
                                )}

                                {/* Risk */}
                                <div style={{
                                    textAlign: 'center',
                                    padding: 'var(--spacing-lg)',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: 'var(--border-radius)',
                                    marginBottom: 'var(--spacing-lg)'
                                }}>
                                    <span className={`risk-badge ${result.risk?.level?.toLowerCase()}`}>
                                        {result.risk?.level}
                                    </span>
                                    <p style={{ marginTop: 'var(--spacing-sm)', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                        {result.risk?.message}
                                    </p>
                                </div>

                                {/* Metrics */}
                                {activeTab === 'dem' && result.water_flow && (
                                    <div className="sensor-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Submerged Area</div>
                                            <div className="sensor-value">{result.water_flow.submerged_area_m2?.toLocaleString()}</div>
                                            <span className="sensor-unit">m²</span>
                                        </div>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Overflow Rate</div>
                                            <div className="sensor-value">{result.water_flow.overflow_rate_m3_per_s?.toFixed(1)}</div>
                                            <span className="sensor-unit">m³/s</span>
                                        </div>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Flow Velocity</div>
                                            <div className="sensor-value">{result.water_flow.avg_flow_velocity_m_per_s?.toFixed(2)}</div>
                                            <span className="sensor-unit">m/s</span>
                                        </div>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Volume</div>
                                            <div className="sensor-value">{result.water_flow.submerged_volume_m3?.toLocaleString()}</div>
                                            <span className="sensor-unit">m³</span>
                                        </div>
                                    </div>
                                )}

                                {activeTab === 'motion' && result.analysis && (
                                    <div className="sensor-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Frames Analyzed</div>
                                            <div className="sensor-value">{result.analysis.frames_analyzed}</div>
                                        </div>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Avg Flow Volume</div>
                                            <div className="sensor-value">{result.analysis.avg_flow_volume_m3?.toFixed(2)}</div>
                                            <span className="sensor-unit">m³</span>
                                        </div>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Max Flow Volume</div>
                                            <div className="sensor-value">{result.analysis.max_flow_volume_m3?.toFixed(2)}</div>
                                            <span className="sensor-unit">m³</span>
                                        </div>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Flow Velocity</div>
                                            <div className="sensor-value">{result.analysis.avg_flow_velocity?.toFixed(2)}</div>
                                            <span className="sensor-unit">m/s</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
