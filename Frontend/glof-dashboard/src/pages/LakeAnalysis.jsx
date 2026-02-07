import { useState, useRef } from 'react';
import { Upload, Waves, TrendingUp, TrendingDown, Snowflake, X, FileImage, AlertTriangle } from 'lucide-react';
import Header from '../components/Header';
import api from '../services/api';

export default function LakeAnalysis() {
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

    const handleAnalyze = async () => {
        if (!file) return;
        setLoading(true);
        const analysisResult = await api.analyzeLake(file);
        setResult(analysisResult);
        setLoading(false);
    };

    const clearFile = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
    };

    const getChangeIndicator = (change) => {
        if (change > 0) return { icon: TrendingUp, color: 'var(--color-danger)', text: `+${change.toFixed(1)}%` };
        if (change < 0) return { icon: TrendingDown, color: 'var(--color-success)', text: `${change.toFixed(1)}%` };
        return { icon: null, color: 'var(--text-secondary)', text: '0%' };
    };

    return (
        <>
            <Header title="Lake Size Analysis" />
            <div className="page-content">
                <div className="grid grid-2">
                    {/* Upload Section */}
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">Upload Satellite Image</span>
                        </div>

                        {!file ? (
                            <div
                                className="upload-zone"
                                onDrop={(e) => { e.preventDefault(); handleFileSelect({ target: { files: e.dataTransfer.files } }); }}
                                onDragOver={(e) => e.preventDefault()}
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <Waves size={48} className="upload-zone-icon" />
                                <p className="upload-zone-text">
                                    <span>Click to upload</span> or drag and drop
                                </p>
                                <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: 'var(--spacing-sm)' }}>
                                    Optical satellite images (Sentinel-2, Landsat)
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
                                <div style={{ position: 'relative', marginBottom: 'var(--spacing-md)' }}>
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
                                </div>

                                <button
                                    className="btn btn-primary"
                                    onClick={handleAnalyze}
                                    disabled={loading}
                                    style={{ width: '100%' }}
                                >
                                    {loading ? 'Analyzing...' : 'Analyze Lake'}
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
                                <Waves size={48} style={{ color: 'var(--text-tertiary)', marginBottom: 'var(--spacing-md)' }} />
                                <p>Upload a satellite image to analyze lake size</p>
                            </div>
                        ) : (
                            <div>
                                {result.mock && (
                                    <div className="alert-banner info" style={{ marginBottom: 'var(--spacing-md)' }}>
                                        <AlertTriangle size={16} />
                                        <span style={{ fontSize: '0.875rem' }}>Mock data</span>
                                    </div>
                                )}

                                {/* Risk Badge */}
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

                                {/* Lake Stats */}
                                <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 'var(--spacing-sm)',
                                        marginBottom: 'var(--spacing-md)'
                                    }}>
                                        <Waves size={18} style={{ color: 'var(--color-primary)' }} />
                                        <span style={{ fontWeight: '600' }}>Lake Coverage</span>
                                    </div>

                                    <div className="sensor-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Before</div>
                                            <div className="sensor-value">{(result.lake?.size_before_m2 / 1000).toFixed(1)}</div>
                                            <span className="sensor-unit">km²</span>
                                        </div>
                                        <div className="sensor-item">
                                            <div className="sensor-label">After</div>
                                            <div className="sensor-value">{(result.lake?.size_after_m2 / 1000).toFixed(1)}</div>
                                            <span className="sensor-unit">km²</span>
                                        </div>
                                    </div>

                                    <div style={{
                                        marginTop: 'var(--spacing-md)',
                                        padding: 'var(--spacing-sm)',
                                        background: result.lake?.change_percent > 5 ? '#fef2f2' : '#f0fdf4',
                                        borderRadius: 'var(--border-radius-sm)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 'var(--spacing-sm)'
                                    }}>
                                        {(() => {
                                            const indicator = getChangeIndicator(result.lake?.change_percent);
                                            return (
                                                <>
                                                    {indicator.icon && <indicator.icon size={16} style={{ color: indicator.color }} />}
                                                    <span style={{ color: indicator.color, fontWeight: '600' }}>
                                                        Change: {indicator.text}
                                                    </span>
                                                </>
                                            );
                                        })()}
                                    </div>
                                </div>

                                {/* Ice Stats */}
                                <div>
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 'var(--spacing-sm)',
                                        marginBottom: 'var(--spacing-md)'
                                    }}>
                                        <Snowflake size={18} style={{ color: 'var(--color-info)' }} />
                                        <span style={{ fontWeight: '600' }}>Ice Coverage</span>
                                    </div>

                                    <div className="sensor-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
                                        <div className="sensor-item">
                                            <div className="sensor-label">Before</div>
                                            <div className="sensor-value">{(result.ice?.size_before_m2 / 1000).toFixed(1)}</div>
                                            <span className="sensor-unit">km²</span>
                                        </div>
                                        <div className="sensor-item">
                                            <div className="sensor-label">After</div>
                                            <div className="sensor-value">{(result.ice?.size_after_m2 / 1000).toFixed(1)}</div>
                                            <span className="sensor-unit">km²</span>
                                        </div>
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
