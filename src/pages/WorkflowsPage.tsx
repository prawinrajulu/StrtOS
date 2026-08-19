import React, { useState, useEffect } from 'react';
import { workflowsApi } from '../services/workflowsApi';
import type { Workflow } from '../services/workflowsApi';
import { clientsApi } from '../services/clientsApi';
import type { Client } from '../services/clientsApi';
import { Network, Plus, ChevronRight, Activity, X } from 'lucide-react';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

interface WorkflowsPageProps {
  onSelectWorkflow?: (workflow: Workflow) => void;
}

export const WorkflowsPage: React.FC<WorkflowsPageProps> = ({ onSelectWorkflow }) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ client_id: '', title: '', directive: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [wfData, clientData] = await Promise.all([
        workflowsApi.listWorkflows(),
        clientsApi.listClients(),
      ]);
      setWorkflows(wfData || []);
      setClients(clientData || []);
      if (clientData && clientData.length > 0) {
        setFormData(prev => ({ ...prev, client_id: clientData[0].id }));
      }
    } catch {
      setWorkflows([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSaving(true);
      const created = await workflowsApi.createWorkflow(formData);
      if (created && created.id) await workflowsApi.startWorkflow(created.id);
      setShowModal(false);
      setFormData({ client_id: clients[0]?.id || '', title: '', directive: '' });
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to create workflow');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Network className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Workflows</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Track business work currently being processed.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center space-x-2 transition"
        >
          <Plus className="w-4 h-4" />
          <span>New Business Request</span>
        </button>
      </div>

      {/* Workflow List */}
      {loading ? (
        <p className="text-xs text-[#92929A]">Loading workflows...</p>
      ) : workflows.length === 0 ? (
        <div className="p-8 bg-[#111113] border border-white/[0.06] rounded-xl text-center space-y-3">
          <p className="text-xs text-[#92929A]">No current data.</p>
          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-[#151518] hover:bg-slate-800 text-slate-200 border border-white/10 transition"
          >
            Submit First Request
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workflows.map((wf) => (
            <div
              key={wf.id}
              onClick={() => onSelectWorkflow && onSelectWorkflow(wf)}
              className="p-5 bg-[#111113] border border-white/[0.06] hover:border-white/15 rounded-xl cursor-pointer transition space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex justify-between items-start">
                  <h3 className="text-sm font-semibold text-[#F5F5F5]">{mapInternalExecutionToBusinessLanguage(wf.title)}</h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-950 text-sky-300 border border-sky-800">
                    {wf.status}
                  </span>
                </div>

                {wf.directive && (
                  <p className="text-xs text-[#92929A] line-clamp-2">
                    {wf.directive}
                  </p>
                )}

                {/* Progress Bar */}
                <div className="space-y-1 pt-1">
                  <div className="flex justify-between text-[10px] font-mono text-[#92929A]">
                    <span>Progress</span>
                    <span>{wf.progress}%</span>
                  </div>
                  <div className="w-full bg-[#151518] rounded-full h-1.5 border border-white/10">
                    <div className="bg-sky-500 h-1.5 rounded-full transition-all" style={{ width: `${wf.progress}%` }} />
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-white/5 flex justify-between items-center text-xs">
                <div className="flex items-center space-x-1 text-emerald-400 font-mono text-[10px]">
                  <Activity className="w-3.5 h-3.5" />
                  <span>Confidence: {wf.confidence_score}%</span>
                </div>
                <div className="flex items-center space-x-1 text-sky-400 font-mono text-[10px] hover:underline">
                  <span>View Workspace</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* New Request Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-[#111113] border border-white/10 rounded-xl max-w-md w-full p-6 space-y-4 text-slate-100">
            <div className="flex justify-between items-center">
              <h2 className="text-base font-bold text-[#F5F5F5]">New Business Request</h2>
              <X className="w-4 h-4 text-[#92929A] cursor-pointer hover:text-slate-200" onClick={() => setShowModal(false)} />
            </div>

            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="text-[#92929A] block mb-1">Target Account</label>
                <select
                  required
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                  className="w-full bg-[#151518] border border-white/10 rounded-lg p-2 text-[#F5F5F5] outline-none"
                >
                  {clients.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[#92929A] block mb-1">Request Title *</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Business Performance & Growth Analysis"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full bg-[#151518] border border-white/10 rounded-lg p-2 text-[#F5F5F5] outline-none"
                />
              </div>

              <div>
                <label className="text-[#92929A] block mb-1">Strategic Objective / Instructions</label>
                <textarea
                  rows={3}
                  placeholder="Provide details for StrtOS to analyze..."
                  value={formData.directive}
                  onChange={(e) => setFormData({ ...formData, directive: e.target.value })}
                  className="w-full bg-[#151518] border border-white/10 rounded-lg p-2 text-[#F5F5F5] outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-2 rounded-lg bg-[#151518] text-[#92929A] border border-white/10 hover:text-[#F5F5F5] transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold transition"
                >
                  {saving ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
