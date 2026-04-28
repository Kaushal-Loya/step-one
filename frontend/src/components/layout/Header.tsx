import { useAppStore } from '../../context/AppContext';
import { useNavigate } from 'react-router-dom';
import './Header.css';

export default function Header() {
  const { toggleSidebar } = useAppStore();
  const navigate = useNavigate();

  return (
    <header className="header">
      <div className="header-left">
        <button className="hamburger" onClick={toggleSidebar}>
          ☰
        </button>
        <div className="header-brand" onClick={() => navigate('/')}>
          Content & Design Engine
        </div>
      </div>
      <div className="header-right">
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
          Dashboard
        </button>
        <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
          Get Started
        </button>
      </div>
    </header>
  );
}
