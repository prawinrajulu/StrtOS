import React, { useState } from 'react';
import {
  ArrowLeft, Globe, DollarSign, Target, Activity,
  Play, Mail, Phone, User, Calendar, CheckCircle2
} from 'lucide-react';
import type { Client } from '../services/clientsApi';
import { CEOApiService } from '../services/ceoApi';

interface ClientDetailsPageProps {
  client: Client;
  onBack: () => void;
  onRunAnalysis: (workflowId: string) => void;
}

export const ClientDetailsPage: React.FC<ClientDetailsPageProps> = ({ client, onBack, onRunAnalysis }) => {
  const [running, setRunning] = useState(false);
  const [directiveText, setDirectiveText] = useState(
    client.business_goal || `Execute full multi-channel customer acquisition strategy for ${client.name} in ${client.industry}.`
  );

  const handleRunCEO = async () => {
    setRunning(true);
    const result = await CEOApiService.submitDirective(directiveText, client.name, client.id);
    setRunning(false);
    if (result && result.workflow_id) {
      onRunAnalysis(result.workflow_id);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Navigation */}
      <button
        onClick={onBack}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'none',
          border: 'none',
          color: '#9ca3af',
          fontSize: '14px',
          cursor: 'pointer',
          marginBottom: '20px'
        }}
      >
        <ArrowLeft size={16} /> Back to Client Portfolio
      </button>

      {/* Header Banner */}
      <div
        style={{
          backgroundColor: '#111827',
          border: '1px solid #1f2937',
          borderRadius: '16px',
          padding: '28px',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '20px'
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#f9fafb', margin: 0 }}>{client.name}</h1>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '12px', fontSize: '12px', fontWeight: '600' }}>
              {client.industry}
            </span>
          </div>

          <div style={{ display: 'flex', gap: '20px', color: '#9ca3af', fontSize: '14px', flexWrap: 'wrap', marginTop: '12px' }}>
            {client.website_url && (
              <a href={client.website_url} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#6366f1', textDecoration: 'none' }}>
                <Globe size={16} /> {client.website_url}
              </a>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10b981' }}>
              <DollarSign size={16} /> Budget: ${client.monthly_budget ? client.monthly_budget.toLocaleString() : '0'} {client.currency} /mo
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Activity size={16} style={{ color: '#f59e0b' }} /> Health Score: {client.health_score}/100
            </div>
          </div>
        </div>

        {/* CEO Analysis Action Button */}
        <button
          onClick={handleRunCEO}
          disabled={running}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '14px 24px',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: '10px',
            fontWeight: '700',
            fontSize: '15px',
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(16, 185, 129, 0.3)',
            transition: 'all 0.2s'
          }}
        >
          <Play size={18} />
          {running ? 'Initializing Orchestration...' : 'Run CEO Analysis'}
        </button>
      </div>

      {/* Grid Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Left Column: Business Brief */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Target style={{ color: '#8b5cf6' }} size={20} /> Business Objective / Directive Directive
            </h3>
            <textarea
              rows={4}
              value={directiveText}
              onChange={(e) => setDirectiveText(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#f3f4f6',
                fontSize: '14px',
                lineHeight: '1.5',
                resize: 'vertical'
              }}
            />
          </div>

          <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '14px' }}>Executive Workflows & Agent Activity</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ padding: '14px', backgroundColor: '#1f2937', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: '600', color: '#f9fafb', fontSize: '14px' }}>Initial Growth Analysis Workflow</div>
                  <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '2px' }}>5 Specialist Agents assigned</div>
                </div>
                <span style={{ fontSize: '12px', color: '#10b981', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CheckCircle2 size={14} /> Ready to Run
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Contact Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '16px' }}>Account Information</h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '14px', color: '#d1d5db' }}>
              {client.contact_name && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <User size={16} style={{ color: '#8b5cf6' }} /> {client.contact_name}
                </div>
              )}
              {client.contact_email && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Mail size={16} style={{ color: '#8b5cf6' }} /> {client.contact_email}
                </div>
              )}
              {client.contact_phone && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Phone size={16} style={{ color: '#8b5cf6' }} /> {client.contact_phone}
                </div>
              )}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingTop: '10px', borderTop: '1px solid #1f2937', color: '#9ca3af', fontSize: '12px' }}>
                <Calendar size={14} /> Created {new Date(client.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
