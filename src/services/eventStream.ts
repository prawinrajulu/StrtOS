export interface RealtimeEventData {
  event_id: string;
  event_type: string;
  workflow_id?: string;
  task_id?: string;
  agent_name?: string;
  organization_id?: string;
  timestamp: string;
  status?: string;
  progress?: number;
  message?: string;
  metadata?: Record<string, any>;
}

export type EventCallback = (event: RealtimeEventData) => void;

export class EventStreamClient {
  private eventSource: EventSource | null = null;
  private listeners: Set<EventCallback> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 6;
  private reconnectTimeout: any = null;
  private url: string;

  constructor(url: string) {
    this.url = url;
  }

  public connect() {
    const token = localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');
    const connectUrl = token ? `${this.url}?token=${encodeURIComponent(token)}` : this.url;

    try {
      this.eventSource = new EventSource(connectUrl);

      this.eventSource.onopen = () => {
        this.reconnectAttempts = 0;
      };

      this.eventSource.onmessage = (e) => {
        try {
          const parsed: RealtimeEventData = JSON.parse(e.data);
          this.listeners.forEach(cb => cb(parsed));
        } catch (err) {
          console.warn('Error parsing SSE event', err);
        }
      };

      this.eventSource.onerror = () => {
        this.disconnect();
        this.scheduleReconnect();
      };
    } catch (e) {
      console.warn('Failed initializing EventSource', e);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      const delay = Math.min(30000, Math.pow(2, this.reconnectAttempts) * 1000);
      this.reconnectAttempts++;
      this.reconnectTimeout = setTimeout(() => this.connect(), delay);
    }
  }

  public subscribe(callback: EventCallback): () => void {
    this.listeners.add(callback);
    if (!this.eventSource) {
      this.connect();
    }
    return () => {
      this.listeners.delete(callback);
      if (this.listeners.size === 0) {
        this.disconnect();
      }
    };
  }

  public disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

export const globalEventStream = new EventStreamClient('/api/v1/ceo/stream');
