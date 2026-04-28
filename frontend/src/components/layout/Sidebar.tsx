
import { useNavigate, useLocation } from 'react-router-dom';
import './Sidebar.css';
import { useAppStore } from '@/context/AppContext';

const menuItems = [
  { id: 'home', label: 'HOME', icon: '🏠', path: '/' },
  { id: 'dashboard', label: 'DASHBOARD', icon: '📊', path: '/dashboard' },
  { id: 'sessions', label: 'SESSIONS', icon: '📋', path: '/sessions' },
  { id: 'outputs', label: 'OUTPUTS', icon: '🖼️', path: '/outputs' },
  { id: 'docs', label: 'API DOCS', icon: '📖', path: '/docs' },
];

export default function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useAppStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleNav = (path: string, id: string) => {
    navigate(path);
    if (window.innerWidth < 768) toggleSidebar();
  };

  return (
    <>
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={toggleSidebar} />
      )}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">C&D Engine</div>
          <button className="sidebar-close" onClick={toggleSidebar}>✕</button>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <button
              key={item.id}
              className={`sidebar-item ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => handleNav(item.path, item.id)}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span className="sidebar-label">{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-version">v1.0.0</div>
        </div>
      </aside>
    </>
  );
}
