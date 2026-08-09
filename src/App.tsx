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
import { ClientsPage } from './pages/ClientsPage';
import { ClientDetailsPage } from './pages/ClientDetailsPage';
import type { Client } from './services/clientsApi';
import { WorkflowsPage } from './pages/WorkflowsPage';
import { WorkflowDetailsPage } from './pages/WorkflowDetailsPage';
import type { Workflow } from './services/workflowsApi';
import { ReportsPage } from './pages/ReportsPage';
import { ReportDetailsPage } from './pages/ReportDetailsPage';
import type { ExecutiveReport } from './services/reportsApi';
import { GlobalFAB } from './components/GlobalFAB';

const MainLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('ai-agents');
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [selectedReport, setSelectedReport] = useState<ExecutiveReport | null>(null);

  const getBreadcrumbs = () => {
    switch (activeTab) {
      case 'dashboard':
        return ['STRTOS', 'Dashboard'];
      case 'clients':
        return selectedClient ? ['STRTOS', 'Clients', selectedClient.name] : ['STRTOS', 'Clients'];
      case 'workflows':
        return selectedWorkflow ? ['STRTOS', 'Workflows', selectedWorkflow.title] : ['STRTOS', 'Workflows'];
      case 'reports':
        return selectedReport ? ['STRTOS', 'Reports', selectedReport.title] : ['STRTOS', 'Reports'];
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
      case 'clients':
        if (selectedClient) {
          return (
            <ClientDetailsPage
              client={selectedClient}
              onBack={() => setSelectedClient(null)}
              onRunAnalysis={() => {
                setActiveTab('ceo-agent');
              }}
            />
          );
        }
        return <ClientsPage onSelectClient={(client) => setSelectedClient(client)} />;
      case 'workflows':
        if (selectedWorkflow) {
          return (
            <WorkflowDetailsPage
              workflow={selectedWorkflow}
              onBack={() => setSelectedWorkflow(null)}
            />
          );
        }
        return <WorkflowsPage onSelectWorkflow={(wf) => setSelectedWorkflow(wf)} />;
      case 'reports':
        if (selectedReport) {
          return (
            <ReportDetailsPage
              report={selectedReport}
              onBack={() => setSelectedReport(null)}
            />
          );
        }
        return <ReportsPage onSelectReport={(rep) => setSelectedReport(rep)} />;
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
