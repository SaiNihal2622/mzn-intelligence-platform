import { LayoutDashboard, Info, BookOpen, Settings, HelpCircle } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
    const navItems = [
        { id: 'analysis', label: 'Project Analysis', icon: LayoutDashboard },
        { id: 'about', label: 'About System', icon: Info },
        { id: 'docs', label: 'Documentation', icon: BookOpen },
    ];

    const bottomItems = [
        { id: 'settings', label: 'Settings', icon: Settings },
        { id: 'help', label: 'Help & Support', icon: HelpCircle },
    ];

    return (
        <div className="sidebar">
            <div className="sidebar-brand">
                <h1 className="sidebar-title">MzN Identity</h1>
                <p className="sidebar-subtitle">Intelligence Platform</p>
            </div>

            <nav className="sidebar-nav">
                <button
                    className={`nav-item ${activeTab === 'analysis' ? 'active' : ''}`}
                    onClick={() => setActiveTab('analysis')}
                >
                    <span className="nav-icon">📊</span>
                    Project Analysis
                </button>
                <button
                    className={`nav-item ${activeTab === 'architecture' ? 'active' : ''}`}
                    onClick={() => setActiveTab('architecture')}
                >
                    <span className="nav-icon">🏗️</span>
                    Architecture
                </button>
                <button
                    className={`nav-item ${activeTab === 'workflow' ? 'active' : ''}`}
                    onClick={() => setActiveTab('workflow')}
                >
                    <span className="nav-icon">📈</span>
                    Workflow Insights
                </button>
            </nav>

            <div className="sidebar-bottom">
                {bottomItems.map((item) => (
                    <button key={item.id} className="sidebar-link">
                        <item.icon />
                        <span>{item.label}</span>
                    </button>
                ))}

                <div className="user-profile">
                    <div className="user-avatar">C</div>
                    <div className="user-info">
                        <p className="user-name">Consultant</p>
                        <p className="user-role">Workspace Access</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
