import type { RealtimeEventData } from './eventStream';
import type { Workflow, TaskItem } from './workflowsApi';

export type UserTaskStatus =
  | 'ANALYZING'
  | 'EVALUATING'
  | 'SYNTHESIZING'
  | 'WAITING_FOR_APPROVAL'
  | 'EXECUTING'
  | 'COMPLETED'
  | 'FAILED'
  | 'DEGRADED';

export interface SubStepItem {
  title: string;
  status: 'COMPLETED' | 'RUNNING' | 'UPCOMING';
}

export interface UserFacingTask {
  id: string;
  title: string;
  status: UserTaskStatus;
  statusMessage?: string;
  progress?: number;
  subSteps: string[];
  subStepDetails?: SubStepItem[];
  currentStep?: string;
  timestamp: string;
  summary?: string;
  confidence?: number;
  recommendedNextStep?: string;
  details?: any;
}

const KNOWN_BUSINESS_MAP: Record<string, string> = {
  BusinessAnalysisAgent: 'Business Performance Analysis',
  BusinessAnalysis: 'Business Performance Analysis',
  'BUSINESS ANALYSIS': 'Business Performance Analysis',
  BUSINESS: 'Business Performance Analysis',
  SEOAuditAgent: 'Website Performance Analysis',
  SEOAudit: 'Website Performance Analysis',
  SEO: 'Website Performance Analysis',
  CompetitorResearchAgent: 'Market Intelligence',
  CompetitorResearch: 'Market Intelligence',
  'COMPETITOR RESEARCH': 'Market Intelligence',
  COMPETITOR: 'Market Intelligence',
  'COMPETITOR SCOUT': 'Market Intelligence',
  MarketingStrategyAgent: 'Strategic Planning',
  MarketingStrategy: 'Strategic Planning',
  'MARKETING STRATEGY': 'Strategic Planning',
  MARKETING: 'Strategic Planning',
  'MARKETING STRATEGIST': 'Strategic Planning',
  CampaignPlannerAgent: 'Campaign Preparation',
  CampaignPlanner: 'Campaign Preparation',
  'CAMPAIGN PLANNER': 'Campaign Preparation',
  CAMPAIGN: 'Campaign Preparation',
  PredictionAgent: 'Strategic Forecast',
  ExecutionAgent: 'Mission Execution',
  SwarmConsensus: 'Recommendation Validation',
  SwarmAgent: 'Recommendation Validation',
  CEOAgent: 'Executive Alignment',
  'CEO Agent': 'Executive Alignment',
  'CEO AGENT': 'Executive Alignment',
  'CEO Orchestrator': 'Executive Alignment',
  PolicyEvolutionAgent: 'Policy Governance Validation',
  AnalyticsAgent: 'Intelligence Reporting',
  ANALYTICS: 'Intelligence Reporting',
  ReportGeneratorAgent: 'Intelligence Reporting',
  REPORT: 'Intelligence Reporting',
  ClientOnboardingAgent: 'Business Onboarding',
  'CLIENT BRIEF': 'Business Onboarding'
};

const TECHNICAL_EVENT_TO_USER_MESSAGE: Record<string, string> = {
  'agent.started': 'Analyzing business performance',
  'agent.tool.started': 'Collecting verified business information',
  'agent.llm.started': 'Analyzing business information',
  'approval.pending': 'Decision requires your approval',
  'execution.started': 'Executing approved action',
  'execution.completed': 'Mission completed',
  'agent.failed': 'Task could not be completed',
  'task.failed': 'Task could not be completed',
  'workflow.updated': 'Updating strategic workflow state',
  'outcome.recorded': 'Recording outcome'
};

export function mapInternalExecutionToBusinessLanguage(agentName?: string): string {
  if (!agentName) return 'StrtOS Intelligence Task';
  if (KNOWN_BUSINESS_MAP[agentName]) {
    return KNOWN_BUSINESS_MAP[agentName];
  }
  const cleaned = agentName
    .replace(/Agent$/i, '')
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .trim();
  return cleaned || 'StrtOS Intelligence Task';
}

export function mapAgentToBusinessTitle(agentName?: string): string {
  return mapInternalExecutionToBusinessLanguage(agentName);
}

export function mapTechnicalEventToUserMessage(eventType: string, defaultMsg?: string): string {
  if (TECHNICAL_EVENT_TO_USER_MESSAGE[eventType]) {
    return TECHNICAL_EVENT_TO_USER_MESSAGE[eventType];
  }
  if (defaultMsg) {
    return defaultMsg
      .replace(/Agent Running/gi, 'StrtOS is working')
      .replace(/Agent Execution/gi, 'Processing')
      .replace(/Swarm Consensus/gi, 'Recommendation Validation')
      .replace(/Agent Tool Started/gi, 'Collecting verified business information')
      .replace(/LLM Processing/gi, 'Analyzing business information')
      .replace(/Agent Optimization/gi, 'Intelligence Performance')
      .replace(/Workflow Node/gi, 'Task')
      .replace(/Agent Failure/gi, 'Task could not be completed');
  }
  return 'Processing business telemetry';
}

export function translateBackendTaskToUserTask(task: TaskItem): UserFacingTask {
  const title = mapInternalExecutionToBusinessLanguage(task.agent_name || task.title);

  let status: UserTaskStatus = 'ANALYZING';
  let progress: number | undefined = undefined;

  switch (task.status) {
    case 'RUNNING':
      status = 'ANALYZING';
      progress = undefined;
      break;
    case 'COMPLETED':
      status = 'COMPLETED';
      progress = 100;
      break;
    case 'FAILED':
      status = 'FAILED';
      progress = 100;
      break;
    case 'QUEUED':
    case 'WAITING':
    default:
      status = 'EVALUATING';
      progress = undefined;
      break;
  }

  const statusMsg = task.status === 'COMPLETED'
    ? 'Completed successfully'
    : task.status === 'FAILED'
    ? `${title} could not be completed`
    : 'StrtOS is working';

  return {
    id: task.id,
    title,
    status,
    statusMessage: statusMsg,
    progress,
    subSteps: [],
    subStepDetails: [],
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    summary: task.status === 'COMPLETED' ? `${title} completed successfully.` : undefined
  };
}

export function translateWorkflowToTasks(workflow: Workflow, tasks: TaskItem[] = []): {
  activeTask: UserFacingTask | null;
  completedTasks: UserFacingTask[];
  upcomingTasks: UserFacingTask[];
} {
  if (!workflow || !Array.isArray(tasks)) {
    return { activeTask: null, completedTasks: [], upcomingTasks: [] };
  }

  const translated = tasks.map(t => translateBackendTaskToUserTask(t));

  const active = translated.find(t => t.status !== 'COMPLETED' && t.status !== 'FAILED') || null;
  const completed = translated.filter(t => t.status === 'COMPLETED');
  const upcoming = translated.filter(t => t !== active && t.status !== 'COMPLETED' && t.status !== 'FAILED');

  return {
    activeTask: active,
    completedTasks: completed,
    upcomingTasks: upcoming
  };
}

export function translateSSEEventToTaskUpdate(event: RealtimeEventData): Partial<UserFacingTask> {
  const title = mapInternalExecutionToBusinessLanguage(event.agent_name);
  let status: UserTaskStatus = 'ANALYZING';

  if (event.event_type.includes('completed')) {
    status = 'COMPLETED';
  } else if (event.event_type.includes('failed')) {
    status = 'FAILED';
  } else if (event.event_type.includes('approval') || event.event_type.includes('pending')) {
    status = 'WAITING_FOR_APPROVAL';
  } else if (event.event_type.includes('execution')) {
    status = 'EXECUTING';
  }

  const statusMsg = mapTechnicalEventToUserMessage(event.event_type, event.message);

  return {
    id: event.task_id || event.event_id,
    title,
    status,
    statusMessage: statusMsg,
    progress: typeof event.progress === 'number' ? event.progress : (status === 'COMPLETED' ? 100 : undefined),
    summary: event.message ? mapTechnicalEventToUserMessage(event.event_type, event.message) : undefined
  };
}
