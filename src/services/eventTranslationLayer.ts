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
  progress: number;
  subSteps: string[];
  currentStep?: string;
  timestamp: string;
  summary?: string;
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
  SwarmConsensus: 'Strategic Recommendation Validation',
  CEOAgent: 'Executive Alignment & Decisioning',
  PredictionAgent: 'Predictive Intelligence & Forecasting',
  PolicyEvolutionAgent: 'Policy & Governance Validation',
  ExecutionAgent: 'Autonomous Mission Execution'
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

export function translateBackendTaskToUserTask(task: TaskItem): UserFacingTask {
  const title = mapAgentToBusinessTitle(task.agent_name || task.title);

  let status: UserTaskStatus = 'ANALYZING';
  let progress = 0;
  const subSteps: string[] = ['Collecting verified business data', 'Evaluating current trends', 'Preparing strategic insights'];

  switch (task.status) {
    case 'RUNNING':
      status = 'ANALYZING';
      progress = 50;
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
      progress = 10;
      break;
  }

  return {
    id: task.id,
    title,
    status,
    progress,
    subSteps,
    currentStep: subSteps[0],
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    summary: `Task completed using verified business telemetry.`
  };
}

export function translateWorkflowToTasks(workflow: Workflow, tasks: TaskItem[] = []): {
  activeTask: UserFacingTask | null;
  completedTasks: UserFacingTask[];
  upcomingTasks: UserFacingTask[];
} {
  if (!workflow) {
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

  return {
    id: event.task_id || event.event_id,
    title,
    status,
    progress: event.progress || (status === 'COMPLETED' ? 100 : 50),
    summary: event.message || `Event processed by STRtOS Engine.`
  };
}
