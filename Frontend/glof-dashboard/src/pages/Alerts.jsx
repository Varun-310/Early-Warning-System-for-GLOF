import { useState } from 'react';
import { Bell, AlertTriangle, Info, CheckCircle, Send, Phone, MapPin } from 'lucide-react';
import Header from '../components/Header';

export default function Alerts() {
    const [phoneNumber, setPhoneNumber] = useState('');
    const [message, setMessage] = useState('');
    const [sending, setSending] = useState(false);

    const mockAlerts = [
        {
            id: 1,
            type: 'warning',
            title: 'Elevated Water Level',
            message: 'Water level at Station A has risen by 0.8m in the last 2 hours.',
            time: '2 hours ago',
            icon: AlertTriangle
        },
        {
            id: 2,
            type: 'warning',
            title: 'Increased Flow Rate',
            message: 'Flow rate detected above normal threshold at 125 m³/s.',
            time: '4 hours ago',
            icon: AlertTriangle
        },
        {
            id: 3,
            type: 'info',
            title: 'Scheduled Maintenance',
            message: 'Sensor calibration scheduled for tomorrow at 10:00 AM.',
            time: '6 hours ago',
            icon: Info
        }
    ];

    const handleSendAlert = async () => {
        if (!phoneNumber || !message) return;
        setSending(true);
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        setSending(false);
        setPhoneNumber('');
        setMessage('');
        alert('Alert sent successfully! (Mock)');
    };

    return (
        <>
            <Header title="Alerts & Notifications" />
            <div className="page-content">
                <div className="grid grid-2">
                    {/* Alert History */}
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">Recent Alerts</span>
                            <span className="risk-badge moderate">{mockAlerts.length} Active</span>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                            {mockAlerts.map((alert) => (
                                <div
                                    key={alert.id}
                                    className={`alert-banner ${alert.type}`}
                                    style={{ margin: 0 }}
                                >
                                    <alert.icon size={20} />
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: '600', marginBottom: '4px' }}>{alert.title}</div>
                                        <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>{alert.message}</div>
                                        <div style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '4px' }}>{alert.time}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Send Alert */}
                    <div className="card">
                        <div className="card-header">
                            <span className="card-title">Send Emergency Alert</span>
                        </div>

                        <div style={{ marginBottom: 'var(--spacing-md)' }}>
                            <label style={{
                                display: 'block',
                                fontSize: '0.875rem',
                                fontWeight: '500',
                                marginBottom: 'var(--spacing-sm)',
                                color: 'var(--text-secondary)'
                            }}>
                                <Phone size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                                Phone Number
                            </label>
                            <input
                                type="tel"
                                className="input"
                                placeholder="+91 XXXXXXXXXX"
                                value={phoneNumber}
                                onChange={(e) => setPhoneNumber(e.target.value)}
                            />
                        </div>

                        <div style={{ marginBottom: 'var(--spacing-md)' }}>
                            <label style={{
                                display: 'block',
                                fontSize: '0.875rem',
                                fontWeight: '500',
                                marginBottom: 'var(--spacing-sm)',
                                color: 'var(--text-secondary)'
                            }}>
                                Message
                            </label>
                            <textarea
                                className="input"
                                placeholder="Emergency alert message..."
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                rows={4}
                                style={{ resize: 'vertical' }}
                            />
                        </div>

                        <div style={{
                            padding: 'var(--spacing-md)',
                            background: 'var(--bg-secondary)',
                            borderRadius: 'var(--border-radius-sm)',
                            marginBottom: 'var(--spacing-md)'
                        }}>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--spacing-sm)',
                                fontSize: '0.875rem',
                                color: 'var(--text-secondary)'
                            }}>
                                <MapPin size={14} />
                                <span>Alert will include evacuation routes for Uttarakhand region</span>
                            </div>
                        </div>

                        <button
                            className="btn btn-danger"
                            onClick={handleSendAlert}
                            disabled={sending || !phoneNumber || !message}
                            style={{ width: '100%' }}
                        >
                            {sending ? (
                                <>
                                    <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px', borderTopColor: 'white' }}></div>
                                    Sending...
                                </>
                            ) : (
                                <>
                                    <Send size={16} />
                                    Send Emergency Alert
                                </>
                            )}
                        </button>

                        <p style={{
                            fontSize: '0.75rem',
                            color: 'var(--text-tertiary)',
                            textAlign: 'center',
                            marginTop: 'var(--spacing-md)'
                        }}>
                            This will send an SMS via Twilio to the specified number
                        </p>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                    <div className="card-header">
                        <span className="card-title">Quick Actions</span>
                    </div>
                    <div style={{ display: 'flex', gap: 'var(--spacing-md)', flexWrap: 'wrap' }}>
                        <button className="btn btn-secondary">
                            <Bell size={16} />
                            Test Alert System
                        </button>
                        <button className="btn btn-secondary">
                            <CheckCircle size={16} />
                            Mark All as Read
                        </button>
                        <button className="btn btn-secondary">
                            <MapPin size={16} />
                            View Evacuation Routes
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}
