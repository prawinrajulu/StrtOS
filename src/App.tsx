import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Sidebar } from './components/Sidebar';
import { TopNav } from './components/TopNav';
import { AIAgentsPage } from './pages/AIAgentsPage';
import { CEOAgentPage } from './pages/CEOAgentPage';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { ProfilePage } from './pages/ProfilePage';
import { GlobalFAB } from './components/GlobalFAB';

const MainLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('ai-agents');

  const getBreadcrumbs = () => {
    switch (activeTab) {
      case 'dashboard':
        return ['STRTOS', 'Dashboard'];
      case 'ceo-agent':
        return ['STRTOS', 'CEO Agent'];
      case 'profile':
        return ['STRTOS', 'Profile'];
      case 'ai-agents':
      default:
        return ['STRTOS', 'AI Agents'];
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage onOpenCEO={() => setActiveTab('ceo-agent')} />;
      case 'ceo-agent':
        return <CEOAgentPage />;
      case 'profile':
        return <ProfilePage />;
      case 'ai-agents':
      default:
        return <AIAgentsPage />;
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#08080a', color: '#f3f4f6' }}>
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <TopNav breadcrumbs={getBreadcrumbs()} />
        <main style={{ flex: 1 }}>{renderContent()}</main>
      </div>
      <GlobalFAB onClick={() => setActiveTab('ceo-agent')} />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
