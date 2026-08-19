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

export interface UserFacingTask {
  id: string;
  title: string;
  status: UserTaskStatus;
  statusMessage?: string;
  progress?: number; // Real percentage if provided by backend, otherwise undefined (showing "Working...")
  subSteps: string[];
  currentStep?: string;
  timestamp: string;
  summary?: string;
  confidence?: number;
  recommendedNextStep?: string;
  details?: any;
}

const AGENT_TO_BUSINESS_TITLE: Record<string, string> = {
  BusinessAnalysisAgent: 'Business Performance Analysis',
  BusinessAnalysis: 'Business Performance Analysis',
  SEOAuditAgent: 'Website Performance Analysis',
  SEOAudit: 'Website Performance Analysis',
  CompetitorResearchAgent: 'Market Intelligence',
  CompetitorResearch: 'Market Intelligence',
  MarketingStrategyAgent: 'Strategic Planning',
  MarketingStrategy: 'Strategic Planning',
  CampaignPlannerAgent: 'Campaign Preparation',
  CampaignPlanner: 'Campaign Preparation',
  PredictionAgent: 'Strategic Forecast',
  ExecutionAgent: 'Mission Execution',
  SwarmConsensus: 'Recommendation Validation',
  SwarmAgent: 'Recommendation Validation',
  CEOAgent: 'Executive Alignment',
  PolicyEvolutionAgent: 'Policy Governance Validation'
};

const TECHNICAL_EVENT_TO_USER_MESSAGE: Record<string, string> = {
  'agent.started': 'Analyzing business performance',
  'agent.tool.started': 'Collecting business information',
  'agent.llm.started': 'Analyzing information',
  'approval.pending': 'Decision requires your approval',
  'execution.started': 'Executing strategic mission',
  'execution.completed': 'Mission execution completed',
  'agent.failed': 'Task could not be completed',
  'task.failed': 'Task could not be completed',
  'workflow.updated': 'Updating strategic workflow state',
  'outcome.recorded': 'Performance outcome recorded'
};

export function mapAgentToBusinessTitle(agentName?: string): string {
  if (!agentName) return 'Business Intelligence Task';
  if (AGENT_TO_BUSINESS_TITLE[agentName]) {
    return AGENT_TO_BUSINESS_TITLE[agentName];
  }
  return agentName
    .replace(/Agent$/, '')
    .replace(/([A-Z])/g, ' $1')
    .trim();
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
      .replace(/Agent Tool Started/gi, 'Collecting business information')
      .replace(/LLM Processing/gi, 'Analyzing information')
      .replace(/Agent Optimization/gi, 'Intelligence Performance')
      .replace(/Workflow Node/gi, 'Task')
      .replace(/Agent Failure/gi, 'Task could not be completed');
  }
  return 'Processing business telemetry';
}

export function translateBackendTaskToUserTask(task: TaskItem): UserFacingTask {
  const title = mapAgentToBusinessTitle(task.agent_name || task.title);

  let status: UserTaskStatus = 'ANALYZING';
  let progress: number | undefined = undefined;

  switch (task.status) {
    case 'RUNNING':
      status = 'ANALYZING';
      progress = undefined; // Real progress if available, otherwise show indeterminate "Working..."
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
  const title = mapAgentToBusinessTitle(event.agent_name);
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
