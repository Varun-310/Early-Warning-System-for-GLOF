import { useState, useRef } from 'react';
import { Upload, Satellite, CheckCircle, AlertTriangle, FileImage, X } from 'lucide-react';
import Header from '../components/Header';
import api, { MOCK_DATA } from '../services/api';

export default function SARAnalysis() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setResult(null);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            setFile(droppedFile);
            setPreview(URL.createObjectURL(droppedFile));
            setResult(null);
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;
        setLoading(true);
        const analysisResult = await api.analyzeSAR(file);
        setResult(analysisResult);
        setLoading(false);
    };

    const clearFile = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
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

    return (
        <>
            <Header title="SAR Image Analysis" />
            <div className="page-content">
                <div className="grid grid-2">
                    {/* Upload Section */}
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">Upload SAR Image</span>
                        </div>

                        {!file ? (
                            <div
                                className="upload-zone"
                                onDrop={handleDrop}
                                onDragOver={(e) => e.preventDefault()}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <Satellite size={48} className="upload-zone-icon" />
                                <p className="upload-zone-text">
                                    <span>Click to upload</span> or drag and drop
                                </p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: 'var(--spacing-sm)' }}>
                                    Sentinel-1 SAR images (JPG, PNG, TIF)
                                </p>
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept=".jpg,.jpeg,.png,.tif,.tiff"
                                    onChange={handleFileSelect}
                                    style={{ display: 'none' }}
                                />
                            </div>
                        ) : (
                            <div>
                                <div style={{
                                    position: 'relative',
                                    borderRadius: 'var(--border-radius)',
                                    overflow: 'hidden',
                                    marginBottom: 'var(--spacing-md)'
                                }}>
                                    <img
                                        src={preview}
                                        alt="Preview"
                                        style={{
                                            width: '100%',
                                            height: '250px',
                                            objectFit: 'cover',
                                            borderRadius: 'var(--border-radius)'
                                        }}
                                    />
                                    <button
                                        onClick={clearFile}
                                        style={{
                                            position: 'absolute',
                                            top: 'var(--spacing-sm)',
                                            right: 'var(--spacing-sm)',
                                            background: 'rgba(0,0,0,0.5)',
                                            border: 'none',
                                            borderRadius: '50%',
                                            width: '32px',
                                            height: '32px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            cursor: 'pointer',
                                            color: 'white'
                                        }}
                                    >
                                        <X size={16} />
                                    </button>
                                </div>

                                <div style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-sm)',
                                    marginBottom: 'var(--spacing-md)',
                                    padding: 'var(--spacing-sm)',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: 'var(--border-radius-sm)'
                                }}>
                                    <FileImage size={16} style={{ color: 'var(--text-tertiary)' }} />
                                    <span style={{ fontSize: '0.875rem', flex: 1 }}>{file.name}</span>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                                        {(file.size / 1024).toFixed(1)} KB
                                    </span>
                                </div>

                                <button
                                    className="btn btn-primary"
                                    onClick={handleAnalyze}
                                    disabled={loading}
                                    style={{ width: '100%' }}
                                >
                                    {loading ? (
                                        <>
                                            <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            <Satellite size={16} />
                                            Analyze Image
                                        </>
                                    )}
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
                                <Satellite size={48} style={{ color: 'var(--text-tertiary)', marginBottom: 'var(--spacing-md)' }} />
                                <p>Upload a SAR image to see analysis results</p>
                            </div>
                        ) : (
                            <div>
                                {result.mock && (
                                    <div className="alert-banner info" style={{ marginBottom: 'var(--spacing-md)' }}>
                                        <AlertTriangle size={16} />
                                        <span style={{ fontSize: '0.875rem' }}>Mock data - connect backend for real analysis</span>
                                    </div>
                                )}

                                {/* Main Result */}
                                <div style={{
                                    textAlign: 'center',
                                    padding: 'var(--spacing-lg)',
                                    background: `${getRiskColor(result.risk_level)}10`,
                                    borderRadius: 'var(--border-radius)',
                                    marginBottom: 'var(--spacing-lg)'
                                }}>
                                    <div style={{
                                        fontSize: '0.875rem',
                                        color: 'var(--text-secondary)',
                                        marginBottom: 'var(--spacing-sm)'
                                    }}>
                                        Predicted Classification
                                    </div>
                                    <div style={{
                                        fontSize: '1.5rem',
                                        fontWeight: '700',
                                        color: 'var(--text-primary)',
                                        textTransform: 'uppercase',
                                        marginBottom: 'var(--spacing-sm)'
                                    }}>
                                        {result.predicted_class?.replace('_', '-') || 'Unknown'}
                                    </div>
                                    <span className={`risk-badge ${result.risk_level?.toLowerCase()}`}>
                                        {result.risk_level}
                                    </span>
                                </div>

                                {/* Probabilities */}
                                <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                                    <div style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: 'var(--spacing-md)' }}>
                                        Class Probabilities
                                    </div>
                                    {result.probabilities && Object.entries(result.probabilities).map(([cls, prob]) => (
                                        <div key={cls} style={{ marginBottom: 'var(--spacing-sm)' }}>
                                            <div style={{
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                fontSize: '0.875rem',
                                                marginBottom: 'var(--spacing-xs)'
                                            }}>
                                                <span style={{ textTransform: 'capitalize' }}>{cls.replace('_', ' ')}</span>
                                                <span style={{ fontWeight: '600' }}>{prob.toFixed(1)}%</span>
                                            </div>
                                            <div style={{
                                                height: '8px',
                                                background: 'var(--bg-tertiary)',
                                                borderRadius: '4px',
                                                overflow: 'hidden'
                                            }}>
                                                <div style={{
                                                    width: `${prob}%`,
                                                    height: '100%',
                                                    background: cls === result.predicted_class ? 'var(--color-primary)' : 'var(--color-gray-400)',
                                                    borderRadius: '4px',
                                                    transition: 'width 0.5s ease'
                                                }}></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Additional Info */}
                                <div className="sensor-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                                    <div className="sensor-item">
                                        <div className="sensor-label">GLOF Probability</div>
                                        <div className="sensor-value">{result.glof_probability?.toFixed(1)}%</div>
                                    </div>
                                    <div className="sensor-item">
                                        <div className="sensor-label">Confidence</div>
                                        <div className="sensor-value">{result.confidence?.toFixed(1)}%</div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
