import React, { useMemo } from 'react';
import { ReactFlow, Background, Handle, Position } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import type { StatusType } from './StatusBadge';
import { Brain, ShieldCheck, Cpu, Search, Target, Megaphone, Send, BarChart2, FileText } from 'lucide-react';

interface StageNodeData {
  label: string;
  agentName: string;
  status: StatusType;
  iconName: string;
}

const getIcon = (name: string) => {
  switch (name) {
    case 'CLIENT BRIEF': return ShieldCheck;
    case 'EXECUTIVE ALIGNMENT': return Brain;
    case 'BUSINESS': return Cpu;
    case 'SEO': return Search;
    case 'COMPETITOR': return Target;
    case 'MARKETING': return Megaphone;
    case 'CAMPAIGN': return Send;
    case 'ANALYTICS': return BarChart2;
    case 'REPORT': default: return FileText;
  }
};

const CustomStageNode: React.FC<any> = ({ data }) => {
  const nodeData = data as StageNodeData;
  const Icon = getIcon(nodeData.label);

  const getBorderColor = () => {
    switch (nodeData.status) {
      case 'RUNNING':
        return '#00e599';
      case 'THINKING':
        return '#a855f7';
      case 'COMPLETED':
        return '#10b981';
      case 'WAITING':
      default:
        return 'rgba(255, 255, 255, 0.08)';
    }
  };

  const getBgColor = () => {
    switch (nodeData.status) {
      case 'RUNNING':
        return 'rgba(0, 229, 153, 0.15)';
      case 'THINKING':
        return 'rgba(168, 85, 247, 0.15)';
      case 'COMPLETED':
        return 'rgba(16, 185, 129, 0.15)';
      case 'WAITING':
      default:
        return 'rgba(255, 255, 255, 0.02)';
    }
  };

  const getIconColor = () => {
    switch (nodeData.status) {
      case 'RUNNING': return '#00e599';
      case 'THINKING': return '#c084fc';
      case 'COMPLETED': return '#34d399';
      case 'WAITING': default: return '#6b7280';
    }
  };

  const isAnimated = nodeData.status === 'RUNNING' || nodeData.status === 'THINKING';

  return (
    <div
      style={{
        padding: '8px 12px',
        borderRadius: '10px',
        backgroundColor: getBgColor(),
        border: `1px solid ${getBorderColor()}`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '6px',
        minWidth: '80px',
        boxShadow: isAnimated ? `0 0 16px ${getBorderColor()}` : 'none',
        transition: 'all 0.3s ease',
      }}
    >
      <Handle type="target" position={Position.Left} style={{ background: '#4b5563', border: 'none' }} />
      <div
        style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: getIconColor(),
        }}
      >
        <Icon size={16} />
      </div>
      <div
        style={{
          fontSize: '9px',
          fontFamily: "'JetBrains Mono', monospace",
          color: nodeData.status === 'WAITING' ? '#6b7280' : '#ffffff',
          textTransform: 'uppercase',
          textAlign: 'center',
        }}
      >
        {nodeData.label}
      </div>
      <Handle type="source" position={Position.Right} style={{ background: '#4b5563', border: 'none' }} />
    </div>
  );
};

export const WorkflowFlowGraph: React.FC<{ stages: { name: string; agent_name: string; status: StatusType }[] }> = ({ stages }) => {
  const nodeTypes = useMemo(() => ({ stageNode: CustomStageNode }), []);

  const nodes = useMemo(() => {
    return stages.map((stg, idx) => ({
      id: `node-${idx}`,
      type: 'stageNode',
      position: { x: idx * 115, y: 30 },
      data: {
        label: stg.name,
        agentName: stg.agent_name,
        status: stg.status,
        iconName: stg.name,
      },
    }));
  }, [stages]);

  const edges = useMemo(() => {
    return stages.slice(0, -1).map((stg, idx) => {
      const nextStage = stages[idx + 1];
      const isCurrentActive = stg.status === 'RUNNING' || stg.status === 'THINKING';
      return {
        id: `edge-${idx}`,
        source: `node-${idx}`,
        target: `node-${idx + 1}`,
        animated: isCurrentActive || nextStage.status === 'RUNNING',
        style: {
          stroke: stg.status === 'COMPLETED' ? '#10b981' : isCurrentActive ? '#00e599' : '#374151',
          strokeWidth: 2,
        },
      };
    });
  }, [stages]);

  return (
    <div style={{ width: '100%', height: '140px', borderRadius: '8px', overflow: 'hidden' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        panOnDrag={false}
        zoomOnScroll={false}
        nodesDraggable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(255,255,255,0.03)" gap={16} size={1} />
      </ReactFlow>
    </div>
  );
};
