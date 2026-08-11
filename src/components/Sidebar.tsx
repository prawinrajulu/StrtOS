import React from 'react';
import {
  LayoutDashboard,
  Users,
  Bot,
  Cpu,
  GitFork,
  BrainCircuit,
  TrendingUp,
  Target,
  Search,
  Megaphone,
  Calendar,
  FileText,
  BarChart3,
  Settings,
  ChevronDown,
  ShieldCheck,
  Brain,
  Zap,
  Network,
  Activity,
  Compass,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const sections = [
    {
      group: 'MAIN',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'clients', label: 'Clients', icon: Users },
        { id: 'workflows', label: 'Workflows', icon: Bot },
      ],
    },
    {
      group: 'GOVERNANCE',
      items: [
        { id: 'approvals', label: 'Approvals', icon: ShieldCheck },
      ],
    },
    {
      group: 'INTELLIGENCE',
      items: [
        { id: 'business-state', label: 'Continuous Business State', icon: Activity, badgeDot: true },
        { id: 'strategy', label: 'Strategic Control Center', icon: Compass, badgeDot: true },
        { id: 'decision-optimization', label: 'Decision Optimization', icon: Compass, badgeDot: true },
        { id: 'action-candidates', label: 'Action Candidates', icon: Cpu },
        { id: 'action-plan', label: 'Predictive Planning', icon: GitFork },
        { id: 'decision-details', label: 'Decision Explanation', icon: Activity },
        { id: 'knowledge', label: 'Causal Knowledge Graph', icon: GitFork, badgeDot: true },
        { id: 'agent-intelligence', label: 'Agent Intelligence', icon: Cpu, badgeDot: true },
        { id: 'policies', label: 'Policy Evolution', icon: ShieldCheck, badgeDot: true },
        { id: 'experiments', label: 'Experiments & A/B', icon: Activity, badgeDot: true },
        { id: 'learning', label: 'Learning & Adaptation', icon: Activity },
        { id: 'swarm', label: 'Swarm Orchestration', icon: Network },
        { id: 'ceo-agent', label: 'CEO Agent', icon: BrainCircuit },
        { id: 'memory', label: 'Memory', icon: Brain },
        { id: 'outcomes', label: 'Outcomes', icon: Target },
        { id: 'predictions', label: 'Predictions', icon: TrendingUp },
        { id: 'ai-agents', label: 'AI Agents', icon: Bot },
        { id: 'business-analysis', label: 'Business Analysis', icon: TrendingUp },
        { id: 'competitor-research', label: 'Competitor Research', icon: Target },
        { id: 'seo-audit', label: 'SEO Audit', icon: Search },
        { id: 'marketing-strategy', label: 'Marketing Strategy', icon: Megaphone },
        { id: 'campaign-planner', label: 'Campaign Planner', icon: Calendar },
      ],
    },
    {
      group: 'EXECUTION',
      items: [
        { id: 'actions', label: 'Actions', icon: Zap },
      ],
    },
    {
      group: 'OUTPUT',
      items: [
        { id: 'reports', label: 'Reports', icon: FileText },
        { id: 'analytics', label: 'Analytics', icon: BarChart3 },
      ],
    },
    {
      group: 'ACCOUNT',
      items: [{ id: 'settings', label: 'Settings', icon: Settings }],
    },
  ];

  return (
    <aside
      style={{
        width: '260px',
        backgroundColor: '#0b0b0e',
        borderRight: '1px solid rgba(255, 255, 255, 0.06)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100vh',
        position: 'sticky',
        top: 0,
        zIndex: 20,
        userSelect: 'none',
      }}
    >
      <div>
        {/* Top Logo */}
        <div
          style={{
            padding: '20px 24px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: '#6366f1',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 'bold',
              color: '#ffffff',
              fontSize: '14px',
              boxShadow: '0 0 16px rgba(99, 102, 241, 0.5)',
            }}
          >
            S
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#f3f4f6', letterSpacing: '-0.02em' }}>
              StrtOS
            </div>
            <div
              style={{
                fontSize: '9px',
                fontFamily: "'JetBrains Mono', monospace",
                color: '#6b7280',
                letterSpacing: '0.1em',
              }}
            >
              AI OS • V1.6
            </div>
          </div>
        </div>

        {/* Enterprise Selector */}
        <div style={{ padding: '16px 16px 8px 16px' }}>
          <div
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: '8px',
              padding: '10px 12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '6px',
                  backgroundColor: '#00e599',
                  color: '#000000',
                  fontSize: '10px',
                  fontWeight: 'bold',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                AV
              </div>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 600, color: '#e5e7eb' }}>Arcadia Ventures</div>
                <div style={{ fontSize: '9px', color: '#6b7280', fontFamily: "'JetBrains Mono', monospace" }}>
                  ENTERPRISE
                </div>
              </div>
            </div>
            <ChevronDown size={14} color="#6b7280" />
          </div>
        </div>

        {/* Navigation Sections */}
        <div
          style={{
            padding: '12px 16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '20px',
            maxHeight: 'calc(100vh - 210px)',
            overflowY: 'auto',
          }}
        >
          {sections.map((sec) => (
            <div key={sec.group}>
              <div
                style={{
                  fontSize: '9px',
                  fontFamily: "'JetBrains Mono', monospace",
                  color: '#4b5563',
                  letterSpacing: '0.12em',
                  marginBottom: '8px',
                  paddingLeft: '8px',
                }}
              >
                {sec.group}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                {sec.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        width: '100%',
                        padding: '9px 12px',
                        borderRadius: '8px',
                        fontSize: '13px',
                        fontWeight: isActive ? 600 : 400,
                        color: isActive ? '#ffffff' : '#9ca3af',
                        backgroundColor: isActive ? 'rgba(255, 255, 255, 0.08)' : 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Icon size={16} color={isActive ? '#ffffff' : '#6b7280'} />
                        <span>{item.label}</span>
                      </div>
                      {item.badgeDot && (
                        <span
                          style={{
                            width: '6px',
                            height: '6px',
                            borderRadius: '50%',
                            backgroundColor: '#a855f7',
                            boxShadow: '0 0 8px #a855f7',
                          }}
                        />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Health Bar */}
      <div
        style={{
          padding: '16px',
          borderTop: '1px solid rgba(255, 255, 255, 0.04)',
          backgroundColor: 'rgba(0, 0, 0, 0.2)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#00e599' }} />
          <span style={{ fontSize: '11px', fontWeight: 500, color: '#e5e7eb' }}>All systems operational</span>
        </div>
        <div
          style={{
            fontSize: '9px',
            fontFamily: "'JetBrains Mono', monospace",
            color: '#4b5563',
            letterSpacing: '0.05em',
            paddingLeft: '14px',
          }}
        >
          8 AGENTS • 128K CTX
        </div>
      </div>
    </aside>
  );
};
