import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Scanner from './components/Scanner';
import ArgumentBuilder from './components/ArgumentBuilder';
import SubjectsView from './components/SubjectsView';
import AuthoritiesView from './components/AuthoritiesView';
import ChatInterface from './components/ChatInterface';
import IntelCenter from './components/IntelCenter';
import LoginButton from './components/LoginButton';
import { Shield, LayoutDashboard, Search, Activity, AlertTriangle, MessageSquare, Users, UserCheck, TrendingUp, Database } from 'lucide-react';

function NavLink({ to, children, icon: Icon }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link to={to} className={`nav-link ${isActive ? 'active' : ''}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <Icon size={18} />
      {children}
    </Link>
  );
}

function App() {
  return (
    <Router>
      <div className="app-container"> {/* Changed class name */}
        <nav className="sidebar"> {/* Changed class name */}
          <div className="logo"> {/* Added logo div */}
            <Shield size={32} />
            <span>RECAPTURE</span>
          </div>
          <div className="nav-links">
            <NavLink to="/" icon={Users}>Subjects</NavLink>
            <NavLink to="/intel" icon={Database}>Intel Center</NavLink>
            <NavLink to="/authorities" icon={UserCheck}>Authorities</NavLink>
            <NavLink to="/arguments" icon={MessageSquare}>Arguments</NavLink>
            <NavLink to="/success" icon={TrendingUp}>Success Tracking</NavLink>
            <NavLink to="/scanner" icon={Search}>Digital Diet Scanner</NavLink>
          </div>
          <div style={{ marginTop: 'auto' }}>
            <LoginButton />
          </div>
        </nav>

        <main className="main-content"> {/* Changed class name */}
          <Routes>
            <Route path="/" element={<SubjectsView />} />
            <Route path="/intel" element={<IntelCenter />} />
            <Route path="/authorities" element={<AuthoritiesView />} />
            <Route path="/arguments" element={<ArgumentBuilder />} />
            <Route path="/success" element={<Dashboard />} />
            <Route path="/scanner" element={<Scanner />} />
          </Routes>
        </main>
        <ChatInterface />
      </div>
    </Router>
  );
}

export default App;
