import { useState, useEffect } from 'react';
import { Bell, RefreshCw } from 'lucide-react';
import api from '../services/api';

export default function Header({ title }) {
    const [lastUpdate, setLastUpdate] = useState(new Date());
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        // Trigger a refresh - in real app this would refetch data
        await new Promise(resolve => setTimeout(resolve, 500));
        setLastUpdate(new Date());
        setIsRefreshing(false);
    };

    return (
        <header className="header">
            <div>
                <h1 className="header-title">{title}</h1>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '2px' }}>
                    Last updated: {lastUpdate.toLocaleTimeString()}
                </p>
            </div>

            <div className="header-actions">
                <button
                    className="btn btn-secondary"
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                >
                    <RefreshCw size={16} className={isRefreshing ? 'spinning' : ''} />
                    Refresh
                </button>

                <button className="btn btn-secondary" style={{ position: 'relative' }}>
                    <Bell size={16} />
                    <span style={{
                        position: 'absolute',
                        top: '-4px',
                        right: '-4px',
                        width: '18px',
                        height: '18px',
                        background: 'var(--color-danger)',
                        borderRadius: '50%',
                        fontSize: '10px',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: '600'
                    }}>3</span>
                </button>
            </div>
        </header>
    );
}
