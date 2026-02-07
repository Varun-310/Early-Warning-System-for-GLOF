import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Server, Database, Bell, Save, CheckCircle, RefreshCw } from 'lucide-react';
import Header from '../components/Header';

export default function Settings() {
    const [apiUrl, setApiUrl] = useState('http://localhost:8000');
    const [saved, setSaved] = useState(false);
    const [services, setServices] = useState([
        { name: 'API Gateway', port: 8000, status: 'Checking...' },
        { name: 'GLOF Service', port: 8001, status: 'Checking...' },
        { name: 'SAR Service', port: 8002, status: 'Checking...' },
        { name: 'Lake Service', port: 8003, status: 'Checking...' },
        { name: 'Terrain Service', port: 8004, status: 'Checking...' },
    ]);
    const [checking, setChecking] = useState(false);

    useEffect(() => {
        checkAllServices();
    }, []);

    const checkServiceHealth = async (port) => {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000);

            const response = await fetch(`http://localhost:${port}/health`, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (response.ok) {
                return 'Online';
            }
            return 'Offline';
        } catch (error) {
            // Try root endpoint as fallback
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 2000);

                const response = await fetch(`http://localhost:${port}/`, {
                    signal: controller.signal
                });
                clearTimeout(timeoutId);

                if (response.ok) {
                    return 'Online';
                }
            } catch {
                // Ignore
            }
            return 'Offline';
        }
    };

    const checkAllServices = async () => {
        setChecking(true);
        const updatedServices = await Promise.all(
            services.map(async (service) => {
                const status = await checkServiceHealth(service.port);
                return { ...service, status };
            })
        );
        setServices(updatedServices);
        setChecking(false);
    };

    const handleSave = () => {
        localStorage.setItem('apiUrl', apiUrl);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const getStatusColor = (status) => {
        if (status === 'Online') return { bg: '#dcfce7', text: '#166534' };
        if (status === 'Checking...') return { bg: '#e0f2fe', text: '#0369a1' };
        return { bg: '#fef3c7', text: '#92400e' };
    };

    const onlineCount = services.filter(s => s.status === 'Online').length;

    return (
        <>
            <Header title="Settings" />
            <div className="page-content">
                <div className="grid grid-2">
                    {/* API Configuration */}
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">
                                <Server size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
                                API Configuration
                            </span>
                        </div>

                        <div style={{ marginBottom: 'var(--spacing-md)' }}>
                            <label style={{
                                display: 'block',
                                fontSize: '0.875rem',
                                fontWeight: '500',
                                marginBottom: 'var(--spacing-sm)',
                                color: 'var(--text-secondary)'
                            }}>
                                Gateway URL
                            </label>
                            <input
                                type="text"
                                className="input"
                                value={apiUrl}
                                onChange={(e) => setApiUrl(e.target.value)}
                                placeholder="http://localhost:8000"
                            />
                        </div>

                        <button
                            className="btn btn-primary"
                            onClick={handleSave}
                            style={{ width: '100%' }}
                        >
                            {saved ? (
                                <>
                                    <CheckCircle size={16} />
                                    Saved!
                                </>
                            ) : (
                                <>
                                    <Save size={16} />
                                    Save Configuration
                                </>
                            )}
                        </button>
                    </div>

                    {/* Service Status */}
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">
                                <Database size={18} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
                                Service Status
                            </span>
                            <button
                                className="btn btn-secondary"
                                onClick={checkAllServices}
                                disabled={checking}
                                style={{ padding: '6px 12px', fontSize: '0.75rem' }}
                            >
                                <RefreshCw size={14} className={checking ? 'spinning' : ''} />
                                Refresh
                            </button>
                        </div>

                        <div style={{
                            marginBottom: 'var(--spacing-md)',
                            padding: 'var(--spacing-sm) var(--spacing-md)',
                            background: onlineCount === services.length ? '#dcfce7' : 'var(--bg-secondary)',
                            borderRadius: 'var(--border-radius-sm)',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            color: onlineCount === services.length ? '#166534' : 'var(--text-secondary)'
                        }}>
                            {onlineCount} of {services.length} services online
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
                            {services.map((service, index) => {
                                const statusColor = getStatusColor(service.status);
                                return (
                                    <div
                                        key={index}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                            padding: 'var(--spacing-sm) var(--spacing-md)',
                                            background: 'var(--bg-secondary)',
                                            borderRadius: 'var(--border-radius-sm)'
                                        }}
                                    >
                                        <div>
                                            <div style={{ fontWeight: '500', fontSize: '0.875rem' }}>{service.name}</div>
                                            <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                                                Port: {service.port}
                                            </div>
                                        </div>
                                        <span style={{
                                            fontSize: '0.75rem',
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                            background: statusColor.bg,
                                            color: statusColor.text
                                        }}>
                                            {service.status}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>

                        {onlineCount < services.length && (
                            <div className="alert-banner info" style={{ marginTop: 'var(--spacing-md)' }}>
                                <Bell size={16} />
                                <span style={{ fontSize: '0.875rem' }}>
                                    Some services are offline. Run start.bat to start all services.
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}
