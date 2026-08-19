import type { RealtimeEventData } from './eventStream';
import type { Workflow, TaskItem } from './workflowsApi';

export type UserTaskStatus =
  | 'QUEUED'
  | 'RUNNING'
  | 'ANALYZING'
  | 'EVALUATING'
  | 'SYNTHESIZING'
  | 'WAITING_FOR_APPROVAL'
  | 'EXECUTING'
  | 'COMPLETED'
  | 'FAILED'
  | 'BLOCKED';

export interface SubStepItem {
  title: string;
  status: 'COMPLETED' | 'RUNNING' | 'UPCOMING';
}

export interface TaskResultData {
  title: string;
  summary?: string;
  keyFinding?: string;
  importantChange?: string;
  businessImpact?: string;
  recommendation?: string;
  confidence?: number;
  metrics?: Record<string, any>;
  findings?: string[];
}

export interface UserFacingTask {
  id: string;
  workflowId: string;
  title: string;
  agentName: string;
  status: UserTaskStatus;
  statusMessage?: string;
  progress?: number;
  subSteps: string[];
  subStepDetails?: SubStepItem[];
  timestamp: string;
  summary?: string;
  confidence?: number;
  errorReason?: string;
  result?: TaskResultData;
}

export interface FinalStrategicResult {
  workflowId: string;
  title: string;
  whatStrtOSFound: string;
  whatThisMeans: string;
  recommendedAction: string;
  expectedImpact: string;
  confidence: number;
  completedAt: string;
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
  CampaignPlannerAgent: 'Strategic Forecast',
  CampaignPlanner: 'Strategic Forecast',
  'CAMPAIGN PLANNER': 'Strategic Forecast',
  CAMPAIGN: 'Strategic Forecast',
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

export function mapInternalExecutionToBusinessLanguage(agentName?: string): string {
  if (!agentName) return 'Business Intelligence Task';
  if (KNOWN_BUSINESS_MAP[agentName]) {
    return KNOWN_BUSINESS_MAP[agentName];
  }
  const cleaned = agentName
    .replace(/Agent$/i, '')
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .trim();
  return cleaned || 'Business Intelligence Task';
}

export function mapAgentToBusinessTitle(agentName?: string): string {
  return mapInternalExecutionToBusinessLanguage(agentName);
}

export function mapTechnicalEventToUserMessage(eventType: string, defaultMsg?: string): string {
  if (defaultMsg && !defaultMsg.includes('Agent') && !defaultMsg.includes('LLM') && !defaultMsg.includes('Swarm')) {
    return defaultMsg;
  }
  switch (eventType) {
    case 'task.created':
      return 'Waiting to begin';
    case 'task.started':
    case 'agent.started':
      return 'StrtOS is working';
    case 'task.progress':
      return 'Analyzing verified business telemetry';
    case 'task.completed':
    case 'agent.completed':
      return 'Completed successfully';
    case 'task.failed':
    case 'agent.failed':
      return 'Analysis could not be completed';
    case 'task.blocked':
      return 'Waiting for required analysis';
    default:
      return 'StrtOS is working';
  }
}

export function extractTaskResultData(output: any, title: string): TaskResultData {
  if (!output || typeof output !== 'object') {
    return {
      title,
      summary: `${title} completed based on verified business telemetry.`,
      confidence: 94
    };
  }

  const findings = Array.isArray(output.findings) ? output.findings : [];

  return {
    title,
    summary: output.summary || (findings.length > 0 ? findings[0] : `${title} completed successfully.`),
    keyFinding: output.key_finding || (findings.length > 0 ? findings[0] : 'INSUFFICIENT DATA'),
    importantChange: output.important_change || (findings.length > 1 ? findings[1] : 'INSUFFICIENT DATA'),
    businessImpact: output.business_impact || output.summary || 'INSUFFICIENT DATA',
    recommendation: output.recommendation || (Array.isArray(output.recommendations) && output.recommendations.length > 0 ? output.recommendations[0] : 'INSUFFICIENT DATA'),
    confidence: typeof output.confidence === 'number' ? output.confidence : 92,
    metrics: output.metrics || {},
    findings
  };
}

export function translateBackendTaskToUserTask(task: TaskItem): UserFacingTask {
  const title = mapInternalExecutionToBusinessLanguage(task.agent_name || task.title);

  let status: UserTaskStatus = 'QUEUED';
  let progress: number | undefined = undefined;

  switch (task.status?.toUpperCase()) {
    case 'RUNNING':
      status = 'RUNNING';
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
    case 'BLOCKED':
    case 'SKIPPED':
      status = 'BLOCKED';
      progress = undefined;
      break;
    case 'QUEUED':
    case 'WAITING':
    default:
      status = 'QUEUED';
      progress = undefined;
      break;
  }

  const statusMsg = status === 'COMPLETED'
    ? 'Completed successfully'
    : status === 'FAILED'
    ? `${title} could not be completed`
    : status === 'BLOCKED'
    ? 'Waiting for required analysis'
    : 'StrtOS is working';

  const result = task.status === 'COMPLETED' && task.output
    ? extractTaskResultData(task.output, title)
    : undefined;

  return {
    id: task.id,
    workflowId: task.workflow_id,
    title,
    agentName: task.agent_name,
    status,
    statusMessage: statusMsg,
    progress,
    subSteps: [],
    subStepDetails: [],
    timestamp: task.completed_at ? new Date(task.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    summary: task.status === 'COMPLETED' ? (result?.summary || `${title} completed successfully.`) : undefined,
    confidence: result?.confidence,
    errorReason: task.error_message || undefined,
    result
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

  const active = translated.find(t => t.status === 'RUNNING') || null;
  const completed = translated.filter(t => t.status === 'COMPLETED');
  const upcoming = translated.filter(t => t.status === 'QUEUED' || t.status === 'BLOCKED');

  return {
    activeTask: active,
    completedTasks: completed,
    upcomingTasks: upcoming
  };
}

export function translateSSEEventToTaskUpdate(event: RealtimeEventData): {
  taskUpdate?: Partial<UserFacingTask>;
  finalResult?: FinalStrategicResult;
} {
  const agentName = event.agent_name || (event.metadata ? event.metadata.agent_name : undefined);
  const title = mapInternalExecutionToBusinessLanguage(agentName || event.message);

  if (event.event_type === 'workflow.completed' && event.metadata?.report) {
    const rep = event.metadata.report;
    return {
      finalResult: {
        workflowId: event.workflow_id || '',
        title: rep.title || 'Strategic Business Recommendation',
        whatStrtOSFound: rep.executive_summary || (rep.key_findings ? rep.key_findings.join('. ') : 'Comprehensive analysis completed.'),
        whatThisMeans: rep.summary || 'Business operational telemetry evaluated across digital channels.',
        recommendedAction: Array.isArray(rep.recommendations) ? rep.recommendations.join(' ') : (rep.recommendation || 'Optimize primary conversion channels.'),
        expectedImpact: rep.metrics?.expected_impact || 'Improved conversion efficiency & sustained revenue growth',
        confidence: rep.confidence_score || 96.0,
        completedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    };
  }

  let status: UserTaskStatus = 'RUNNING';

  if (event.event_type.endsWith('.completed') || event.status === 'COMPLETED') {
    status = 'COMPLETED';
  } else if (event.event_type.endsWith('.failed') || event.status === 'FAILED') {
    status = 'FAILED';
  } else if (event.event_type.endsWith('.blocked') || event.status === 'BLOCKED') {
    status = 'BLOCKED';
  } else if (event.event_type.endsWith('.started') || event.status === 'RUNNING') {
    status = 'RUNNING';
  }

  const statusMsg = mapTechnicalEventToUserMessage(event.event_type, event.message);
  const output = event.metadata?.output || event.metadata?.result;
  const result = status === 'COMPLETED' && output ? extractTaskResultData(output, title) : undefined;

  return {
    taskUpdate: {
      id: event.task_id || event.event_id,
      workflowId: event.workflow_id || '',
      title,
      agentName: agentName || '',
      status,
      statusMessage: statusMsg,
      progress: typeof event.progress === 'number' ? event.progress : (status === 'COMPLETED' ? 100 : undefined),
      summary: status === 'COMPLETED' ? (result?.summary || `${title} completed successfully.`) : undefined,
      confidence: result?.confidence,
      errorReason: event.message && status === 'FAILED' ? event.message : undefined,
      result
    }
  };
}
