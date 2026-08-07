import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopNav } from './components/TopNav';
import { AIAgentsPage } from './pages/AIAgentsPage';
import { CEOAgentPage } from './pages/CEOAgentPage';
import { DashboardPage } from './pages/DashboardPage';
import { GlobalFAB } from './components/GlobalFAB';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('ai-agents');

  const getBreadcrumbs = () => {
    switch (activeTab) {
      case 'dashboard':
        return ['STRTOS', 'Dashboard'];
      case 'ceo-agent':
        return ['STRTOS', 'CEO Agent'];
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

export default App;
