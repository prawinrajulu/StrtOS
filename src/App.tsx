import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Sidebar } from './components/Sidebar';
import { TopNav } from './components/TopNav';
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
import { ApprovalsPage } from './pages/ApprovalsPage';
import { ApprovalDetailsPage } from './pages/ApprovalDetailsPage';
import type { ApprovalRequest } from './services/governanceApi';
import { MemoryPage } from './pages/MemoryPage';
import { MemoryDetailsPage } from './pages/MemoryDetailsPage';
import { OutcomesPage } from './pages/OutcomesPage';
import type { MemoryRecord } from './services/memoryApi';
import { PredictionsPage } from './pages/PredictionsPage';
import { PredictionDetailsPage } from './pages/PredictionDetailsPage';
import { PredictionSimulatorPage } from './pages/PredictionSimulatorPage';
import type { PredictionRecord } from './services/predictionsApi';
import { ExecutionPage } from './pages/ExecutionPage';
import { ActionDetailsPage } from './pages/ActionDetailsPage';
import type { ActionRecord } from './services/executionApi';
import { ExperimentsPage } from './pages/ExperimentsPage';
import { PolicyDetailsPage } from './pages/PolicyDetailsPage';
import { PoliciesPage } from './pages/PoliciesPage';
import { PolicyEvolutionPage } from './pages/PolicyEvolutionPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { DecisionGraphPage } from './pages/DecisionGraphPage';
import { RootCausePage } from './pages/RootCausePage';
import { DecisionOptimizationPage } from './pages/DecisionOptimizationPage';
import { ActionCandidatesPage } from './pages/ActionCandidatesPage';
import { ActionPlanPage } from './pages/ActionPlanPage';
import { DecisionOptimizationDetailsPage } from './pages/DecisionOptimizationDetailsPage';
import { StrategyPage } from './pages/StrategyPage';
import { BusinessStatePage } from './pages/BusinessStatePage';
import { ForecastingPage } from './pages/ForecastingPage';
import { CommandCenterPage } from './pages/CommandCenterPage';
import { MissionsPage } from './pages/MissionsPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { ResourceControlCenterPage } from './pages/ResourceControlCenterPage';
import { GlobalFAB } from './components/GlobalFAB';

const MainLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('command-center');
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [selectedReport, setSelectedReport] = useState<ExecutiveReport | null>(null);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [selectedMemory, setSelectedMemory] = useState<MemoryRecord | null>(null);
  const [selectedPrediction, setSelectedPrediction] = useState<PredictionRecord | null>(null);
  const [selectedAction, setSelectedAction] = useState<ActionRecord | null>(null);
  const [selectedPolicyId, setSelectedPolicyId] = useState<string | null>(null);
  const [selectedKnowledgeDecision, setSelectedKnowledgeDecision] = useState<string | null>(null);
  const [selectedKnowledgeOutcome, setSelectedKnowledgeOutcome] = useState<string | null>(null);
  const [showSimulator, setShowSimulator] = useState<boolean>(false);

  const getBreadcrumbs = () => {
    switch (activeTab) {
      case 'command-center':
        return ['STRTOS', 'STRtOS Intelligence Engine'];
      case 'dashboard':
        return ['STRTOS', 'Executive Dashboard'];
      case 'business-state':
        return ['STRTOS', 'Business State Intelligence'];
      case 'forecasting':
        return ['STRTOS', 'Strategic Forecasting'];
      case 'strategy':
        return ['STRTOS', 'Strategy Engine'];
      case 'decision-optimization':
        return ['STRTOS', 'Decision Optimization'];
      case 'knowledge':
        return ['STRTOS', 'Knowledge Graph'];
      case 'missions':
        return ['STRTOS', 'Missions'];
      case 'portfolio':
        return ['STRTOS', 'Portfolio Control'];
      case 'workflows':
        return selectedWorkflow ? ['STRTOS', 'Workflows', selectedWorkflow.title] : ['STRTOS', 'Workflows'];
      case 'resources':
        return ['STRTOS', 'Resource Control Center'];
      case 'approvals':
        return selectedApproval ? ['STRTOS', 'Governance', selectedApproval.title] : ['STRTOS', 'Governance', 'Approvals'];
      case 'policies':
        if (selectedPolicyId) return ['STRTOS', 'Governance', 'Policies', 'Details'];
        return ['STRTOS', 'Governance', 'Policies'];
      case 'policy-evolution':
        return ['STRTOS', 'Governance', 'Policies', 'Evolution Pipeline'];
      case 'memory':
        return selectedMemory ? ['STRTOS', 'Insights', 'Memory', selectedMemory.title] : ['STRTOS', 'Insights', 'Memory'];
      case 'outcomes':
        return ['STRTOS', 'Insights', 'Outcomes & Reports'];
      case 'reports':
        return selectedReport ? ['STRTOS', 'Insights', 'Reports', selectedReport.title] : ['STRTOS', 'Insights', 'Reports'];
      case 'clients':
        return selectedClient ? ['STRTOS', 'Business Accounts', selectedClient.name] : ['STRTOS', 'Business Accounts'];
      case 'settings':
      case 'profile':
        return ['STRTOS', 'Settings & System Diagnostics'];
      default:
        return ['STRTOS', 'STRtOS Intelligence Engine'];
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'command-center':
        return <CommandCenterPage />;
      case 'dashboard':
        return <DashboardPage onOpenCEO={() => setActiveTab('command-center')} />;
      case 'business-state':
        return <BusinessStatePage />;
      case 'forecasting':
        return <ForecastingPage />;
      case 'strategy':
        return <StrategyPage />;
      case 'decision-optimization':
        return <DecisionOptimizationPage />;
      case 'action-candidates':
        return <ActionCandidatesPage />;
      case 'action-plan':
        return <ActionPlanPage />;
      case 'decision-details':
        return <DecisionOptimizationDetailsPage />;
      case 'knowledge':
        return (
          <KnowledgePage
            onNavigateToExplainability={(decId) => {
              setSelectedKnowledgeDecision(decId);
              setActiveTab('decision-explainability');
            }}
            onNavigateToRootCause={(outId) => {
              setSelectedKnowledgeOutcome(outId);
              setActiveTab('root-cause');
            }}
          />
        );
      case 'decision-explainability':
        return (
          <DecisionGraphPage
            decisionId={selectedKnowledgeDecision || undefined}
            onBack={() => setActiveTab('knowledge')}
          />
        );
      case 'root-cause':
        return (
          <RootCausePage
            outcomeId={selectedKnowledgeOutcome || undefined}
            onBack={() => setActiveTab('knowledge')}
          />
        );
      case 'missions':
        return <MissionsPage />;
      case 'portfolio':
        return <PortfolioPage />;
      case 'resources':
        return <ResourceControlCenterPage />;
      case 'clients':
        if (selectedClient) {
          return (
            <ClientDetailsPage
              client={selectedClient}
              onBack={() => setSelectedClient(null)}
              onRunAnalysis={() => {
                setActiveTab('command-center');
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
      case 'actions':
        if (selectedAction) {
          return (
            <ActionDetailsPage
              action={selectedAction}
              onBack={() => setSelectedAction(null)}
            />
          );
        }
        return <ExecutionPage onSelectAction={(act) => setSelectedAction(act)} />;
      case 'approvals':
        if (selectedApproval) {
          return (
            <ApprovalDetailsPage
              approval={selectedApproval}
              onBack={() => setSelectedApproval(null)}
              onUpdated={() => {
                setSelectedApproval(null);
              }}
            />
          );
        }
        return <ApprovalsPage onSelectApproval={(app) => setSelectedApproval(app)} />;
      case 'policies':
        if (selectedPolicyId) {
          return (
            <PolicyDetailsPage
              policyId={selectedPolicyId}
              onBack={() => setSelectedPolicyId(null)}
            />
          );
        }
        return (
          <PoliciesPage
            onSelectPolicy={(id) => setSelectedPolicyId(id)}
            onNavigateToEvolution={() => setActiveTab('policy-evolution')}
          />
        );
      case 'policy-evolution':
        return <PolicyEvolutionPage onBack={() => setActiveTab('policies')} />;
      case 'experiments':
        return <ExperimentsPage />;
      case 'memory':
        if (selectedMemory) {
          return (
            <MemoryDetailsPage
              memory={selectedMemory}
              onBack={() => setSelectedMemory(null)}
            />
          );
        }
        return <MemoryPage onSelectMemory={(mem) => setSelectedMemory(mem)} />;
      case 'outcomes':
        return <OutcomesPage />;
      case 'predictions':
        if (showSimulator) {
          return (
            <PredictionSimulatorPage
              onBack={() => setShowSimulator(false)}
              onSelectPrediction={(pred) => {
                setShowSimulator(false);
                setSelectedPrediction(pred);
              }}
            />
          );
        }
        if (selectedPrediction) {
          return (
            <PredictionDetailsPage
              prediction={selectedPrediction}
              onBack={() => setSelectedPrediction(null)}
            />
          );
        }
        return (
          <PredictionsPage
            onSelectPrediction={(pred) => setSelectedPrediction(pred)}
            onOpenSimulator={() => setShowSimulator(true)}
          />
        );
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
      case 'settings':
      case 'profile':
        return <ProfilePage onNavigateDiagnostics={(tab) => setActiveTab(tab)} />;
      default:
        return <CommandCenterPage />;
    }
  };

  return (
    <div className="flex h-screen bg-[#08080a] text-slate-100 overflow-hidden font-sans">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopNav breadcrumbs={getBreadcrumbs()} />
        <main className="flex-1 overflow-y-auto bg-[#08080a]">
          {renderContent()}
        </main>
      </div>
      <GlobalFAB onClick={() => setActiveTab('command-center')} />
    </div>
  );
};

export default function App() {
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
}
