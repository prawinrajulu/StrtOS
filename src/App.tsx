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
import { SwarmPage } from './pages/SwarmPage';
import { SwarmDetailsPage } from './pages/SwarmDetailsPage';
import type { SwarmSessionRecord } from './services/swarmApi';
import { LearningPage } from './pages/LearningPage';
import { ExperimentsPage } from './pages/ExperimentsPage';
import { AgentPerformancePage } from './pages/AgentPerformancePage';
import { PolicyDetailsPage } from './pages/PolicyDetailsPage';
import { PoliciesPage } from './pages/PoliciesPage';
import { PolicyEvolutionPage } from './pages/PolicyEvolutionPage';
import { AgentIntelligencePage } from './pages/AgentIntelligencePage';
import { AgentOptimizationPage } from './pages/AgentOptimizationPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { DecisionGraphPage } from './pages/DecisionGraphPage';
import { RootCausePage } from './pages/RootCausePage';
import { DecisionOptimizationPage } from './pages/DecisionOptimizationPage';
import { ActionCandidatesPage } from './pages/ActionCandidatesPage';
import { ActionPlanPage } from './pages/ActionPlanPage';
import { DecisionOptimizationDetailsPage } from './pages/DecisionOptimizationDetailsPage';
import { StrategyPage } from './pages/StrategyPage';
import { BusinessStatePage } from './pages/BusinessStatePage';
import type { AgentPerformanceRecord } from './services/learningApi';
import { GlobalFAB } from './components/GlobalFAB';

const MainLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('ai-agents');
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [selectedReport, setSelectedReport] = useState<ExecutiveReport | null>(null);
  const [selectedApproval, setSelectedApproval] = useState<ApprovalRequest | null>(null);
  const [selectedMemory, setSelectedMemory] = useState<MemoryRecord | null>(null);
  const [selectedPrediction, setSelectedPrediction] = useState<PredictionRecord | null>(null);
  const [selectedAction, setSelectedAction] = useState<ActionRecord | null>(null);
  const [selectedSwarm, setSelectedSwarm] = useState<SwarmSessionRecord | null>(null);
  const [selectedLearningAgent, setSelectedLearningAgent] = useState<AgentPerformanceRecord | null>(null);
  const [selectedPolicyAgent, setSelectedPolicyAgent] = useState<string | null>(null);
  const [selectedPolicyId, setSelectedPolicyId] = useState<string | null>(null);
  const [selectedKnowledgeDecision, setSelectedKnowledgeDecision] = useState<string | null>(null);
  const [selectedKnowledgeOutcome, setSelectedKnowledgeOutcome] = useState<string | null>(null);
  const [selectedIntelligenceAgent, setSelectedIntelligenceAgent] = useState<string | null>(null);
  const [showSimulator, setShowSimulator] = useState(false);

  const getBreadcrumbs = () => {
    switch (activeTab) {
      case 'dashboard':
        return ['STRTOS', 'Dashboard'];
      case 'knowledge':
        return ['STRTOS', 'Intelligence', 'Causal Knowledge Graph'];
      case 'decision-explainability':
        return ['STRTOS', 'Intelligence', 'Knowledge Graph', 'Decision Explainability'];
      case 'root-cause':
        return ['STRTOS', 'Intelligence', 'Knowledge Graph', 'Outcome Root Cause'];
      case 'agent-intelligence':
        if (selectedIntelligenceAgent) return ['STRTOS', 'Intelligence', 'Agent Performance', selectedIntelligenceAgent];
        return ['STRTOS', 'Intelligence', 'Agent Performance Intelligence'];
      case 'agent-optimization':
        return ['STRTOS', 'Intelligence', 'Optimization Control Center'];
      case 'policies':
        if (selectedPolicyId) return ['STRTOS', 'Intelligence', 'Policy Evolution', 'Details'];
        return ['STRTOS', 'Intelligence', 'Policy Evolution'];
      case 'policy-evolution':
        return ['STRTOS', 'Intelligence', 'Policy Evolution', 'Pipeline'];
      case 'clients':
        return selectedClient ? ['STRTOS', 'Clients', selectedClient.name] : ['STRTOS', 'Clients'];
      case 'workflows':
        return selectedWorkflow ? ['STRTOS', 'Workflows', selectedWorkflow.title] : ['STRTOS', 'Workflows'];
      case 'approvals':
        return selectedApproval ? ['STRTOS', 'Governance', selectedApproval.title] : ['STRTOS', 'Governance', 'Approvals'];
      case 'actions':
        return selectedAction ? ['STRTOS', 'Execution', selectedAction.name] : ['STRTOS', 'Execution', 'Actions'];
      case 'swarm':
        return selectedSwarm ? ['STRTOS', 'Intelligence', 'Swarm', selectedSwarm.objective] : ['STRTOS', 'Intelligence', 'Swarm'];
      case 'learning':
        if (selectedPolicyAgent) return ['STRTOS', 'Intelligence', 'Learning', 'Policies', selectedPolicyAgent];
        if (selectedLearningAgent) return ['STRTOS', 'Intelligence', 'Learning', selectedLearningAgent.agent_name];
        return ['STRTOS', 'Intelligence', 'Learning & Adaptation'];
      case 'memory':
        return selectedMemory ? ['STRTOS', 'Intelligence', 'Memory', selectedMemory.title] : ['STRTOS', 'Intelligence', 'Memory'];
      case 'outcomes':
        return ['STRTOS', 'Intelligence', 'Outcomes'];
      case 'predictions':
        if (showSimulator) return ['STRTOS', 'Intelligence', 'Predictions', 'What-If Simulator'];
        return selectedPrediction ? ['STRTOS', 'Intelligence', 'Predictions', selectedPrediction.scenario_name] : ['STRTOS', 'Intelligence', 'Predictions'];
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
      case 'swarm':
        if (selectedSwarm) {
          return (
            <SwarmDetailsPage
              swarm={selectedSwarm}
              onBack={() => setSelectedSwarm(null)}
            />
          );
        }
        return <SwarmPage onSelectSwarm={(s) => setSelectedSwarm(s)} />;
      case 'learning':
        if (selectedPolicyAgent) {
          return (
            <PolicyDetailsPage
              agentName={selectedPolicyAgent}
              onBack={() => setSelectedPolicyAgent(null)}
            />
          );
        }
        if (selectedLearningAgent) {
          return (
            <AgentPerformancePage
              agent={selectedLearningAgent}
              onBack={() => setSelectedLearningAgent(null)}
            />
          );
        }
        return (
          <LearningPage
            onSelectAgent={(ag) => setSelectedLearningAgent(ag)}
            onOpenPolicies={(agName) => setSelectedPolicyAgent(agName)}
          />
        );
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
      case 'decision-optimization':
        return <DecisionOptimizationPage />;
      case 'action-candidates':
        return <ActionCandidatesPage />;
      case 'action-plan':
        return <ActionPlanPage />;
      case 'decision-details':
        return <DecisionOptimizationDetailsPage />;
      case 'strategy':
        return <StrategyPage />;
      case 'business-state':
        return <BusinessStatePage />;
      case 'agent-intelligence':
        if (selectedIntelligenceAgent) {
          return (
            <AgentPerformancePage
              agentName={selectedIntelligenceAgent}
              onBack={() => setSelectedIntelligenceAgent(null)}
            />
          );
        }
        return (
          <AgentIntelligencePage
            onSelectAgent={(agName) => setSelectedIntelligenceAgent(agName)}
            onNavigateToOptimization={() => setActiveTab('agent-optimization')}
          />
        );
      case 'agent-optimization':
        return <AgentOptimizationPage onBack={() => setActiveTab('agent-intelligence')} />;
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
