import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ArgumentBuilder from './components/ArgumentBuilder';
import SubjectsView from './components/SubjectsView';
import SubjectDetail from './components/SubjectDetail';
import CloneChat from './components/CloneChat';
import AuthoritiesView from './components/AuthoritiesView';
import ChatInterface from './components/ChatInterface';
import IntelCenter from './components/IntelCenter';
import LoginButton from './components/LoginButton';
import CloneDashboard from './components/CloneDashboard';
import { Shield, LayoutDashboard, Search, Activity, AlertTriangle, MessageSquare, Users, UserCheck, TrendingUp, Database, Bot } from 'lucide-react';

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

import LanguageSelector from './components/LanguageSelector';

function App() {
  return (
    <Router>
      <div className="app-container">
        <nav className="sidebar">
          <div className="logo">
            <Shield size={32} />
            <span>RECAPTURE</span>
          </div>
          <div className="nav-links">
            <NavLink to="/" icon={Users}>Subjects</NavLink>
            <NavLink to="/clones" icon={Bot}>Digital Clones</NavLink>
            <NavLink to="/intel" icon={Database}>Intel Center</NavLink>
            <NavLink to="/authorities" icon={UserCheck}>Authorities</NavLink>
            <NavLink to="/arguments" icon={MessageSquare}>Arguments</NavLink>
            <NavLink to="/success" icon={TrendingUp}>Success Tracking</NavLink>
          </div>
          <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <LanguageSelector />
            <LoginButton />
          </div>
        </nav>

        <main className="main-content"> {/* Changed class name */}
          <Routes>
            <Route path="/" element={<SubjectsView />} />
            <Route path="/clones" element={<CloneDashboard />} />
            <Route path="/subjects/:id" element={<SubjectDetail />} />
            <Route path="/subjects/:id/clone" element={<CloneChat />} />
            <Route path="/intel" element={<IntelCenter />} />
            <Route path="/authorities" element={<AuthoritiesView />} />
            <Route path="/arguments" element={<ArgumentBuilder />} />
            <Route path="/success" element={<Dashboard />} />
          </Routes>
        </main>
        <ChatInterface />
      </div>
    </Router>
  );
}

export default App;
