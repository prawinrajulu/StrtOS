import type { StatusType } from '../components/StatusBadge';

export interface TaskData {
  task_id: string;
  title: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  agent_name: string;
  status: StatusType;
  eta: string;
  dependencies: string[];
  confidence: number;
  retry_count: number;
}

export interface WorkflowStageData {
  id: string;
  name: string;
  agent_name: string;
  status: StatusType;
}

export interface ExecutionStateData {
  workflow_id: string;
  client_name: string;
  current_thought: string;
  overall_confidence: number;
  stages: WorkflowStageData[];
  tasks: TaskData[];
  completed_count: number;
  running_count: number;
  waiting_count: number;
  is_active: boolean;
}

export interface SpecialistOutputData {
  agent_name: string;
  title: string;
  findings: string[];
  metrics: Record<string, any>;
  confidence: number;
  warning?: string;
}

export interface ExecutiveReportData {
  workflow_id: string;
  client_name: string;
  directive: string;
  generated_at: string;
  overall_confidence: number;
  business_summary: SpecialistOutputData;
  seo_summary: SpecialistOutputData;
  competitor_summary: SpecialistOutputData;
  marketing_summary: SpecialistOutputData;
  campaign_summary: SpecialistOutputData;
  analytics_summary: SpecialistOutputData;
  ceo_final_recommendations: string[];
}

const BASE_URL = 'http://localhost:8000/api/v1';

export class CEOApiService {
  static async submitDirective(directive: string, clientName = 'Arcadia Ventures'): Promise<void> {
    try {
      await fetch(`${BASE_URL}/directive`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directive, client_name: clientName }),
      });
    } catch (e) {
      console.warn('API offline - running in fallback mode', e);
    }
  }

  static async fetchReport(): Promise<ExecutiveReportData | null> {
    try {
      const res = await fetch(`${BASE_URL}/report`);
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn('Failed fetching executive report', e);
    }
    return null;
  }

  static subscribeToStream(onUpdate: (state: ExecutionStateData) => void): () => void {
    let eventSource: EventSource | null = null;
    try {
      eventSource = new EventSource(`${BASE_URL}/stream`);
      eventSource.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.type === 'STATE_UPDATE' && parsed.data) {
            onUpdate(parsed.data);
          }
        } catch (err) {
          console.error('Error parsing SSE event', err);
        }
      };
    } catch (e) {
      console.warn('SSE subscription failed', e);
    }

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }
}
