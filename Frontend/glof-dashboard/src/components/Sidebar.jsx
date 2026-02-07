import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Satellite,
    Waves,
    Mountain,
    Bell,
    Settings,
    Activity,
    Shield
} from 'lucide-react';

export default function Sidebar() {
    const navItems = [
        { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/sar-analysis', icon: Satellite, label: 'SAR Analysis' },
        { to: '/lake-analysis', icon: Waves, label: 'Lake Analysis' },
        { to: '/terrain-analysis', icon: Mountain, label: 'Terrain Analysis' },
        { to: '/alerts', icon: Bell, label: 'Alerts' },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo">
                    <Shield size={28} />
                    <span>GLOF Monitor</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                <div className="nav-section">
                    <div className="nav-section-title">Main</div>
                    {navItems.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                        >
                            <item.icon size={18} />
                            {item.label}
                        </NavLink>
                    ))}
                </div>

                <div className="nav-section">
                    <div className="nav-section-title">System</div>
                    <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                        <Settings size={18} />
                        Settings
                    </NavLink>
                </div>
            </nav>

            <div style={{ padding: 'var(--spacing-md)', borderTop: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)' }}>
                    <Activity size={14} style={{ color: 'var(--color-success)' }} />
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        System Online
                    </span>
                </div>
            </div>
        </aside>
    );
}
