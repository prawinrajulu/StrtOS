import React, { useState } from 'react';
import { Briefcase, Zap, AlertTriangle, Layers } from 'lucide-react';
import { PortfolioControlCenterPage } from './PortfolioControlCenterPage';
import { PortfolioSimulationPage } from './PortfolioSimulationPage';
import { PortfolioRecommendationsPage } from './PortfolioRecommendationsPage';
import { PortfolioDetailsPage } from './PortfolioDetailsPage';
import type { Portfolio } from '../services/portfolioApi';

export const PortfolioPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'control-center' | 'simulation' | 'recommendations' | 'details'>('control-center');
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);

  return (
    <div className="space-y-4">
      {/* Sub-navigation bar */}
      <div className="flex items-center space-x-2 border-b border-slate-800 px-6 pt-4 text-xs font-mono">
        <button
          onClick={() => setActiveTab('control-center')}
          className={`flex items-center space-x-2 px-4 py-2 border-b-2 font-medium transition-all ${
            activeTab === 'control-center'
              ? 'border-cyan-400 text-cyan-300 bg-slate-900/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Briefcase className="w-4 h-4" />
          <span>Control Center</span>
        </button>

        <button
          onClick={() => setActiveTab('simulation')}
          className={`flex items-center space-x-2 px-4 py-2 border-b-2 font-medium transition-all ${
            activeTab === 'simulation'
              ? 'border-amber-400 text-amber-300 bg-slate-900/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Zap className="w-4 h-4" />
          <span>What-If Simulator</span>
        </button>

        <button
          onClick={() => setActiveTab('recommendations')}
          className={`flex items-center space-x-2 px-4 py-2 border-b-2 font-medium transition-all ${
            activeTab === 'recommendations'
              ? 'border-rose-400 text-rose-300 bg-slate-900/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>Recommendations</span>
        </button>

        <button
          onClick={() => setActiveTab('details')}
          className={`flex items-center space-x-2 px-4 py-2 border-b-2 font-medium transition-all ${
            activeTab === 'details'
              ? 'border-indigo-400 text-indigo-300 bg-slate-900/50'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" />
          <span>Details & Knowledge</span>
        </button>
      </div>

      {/* Render active sub-view */}
      <div>
        {activeTab === 'control-center' && (
          <PortfolioControlCenterPage
            onNavigateToSimulation={() => setActiveTab('simulation')}
            onNavigateToRecommendations={() => setActiveTab('recommendations')}
            onSelectPortfolio={(p) => setSelectedPortfolio(p)}
          />
        )}

        {activeTab === 'simulation' && (
          <PortfolioSimulationPage
            onBack={() => setActiveTab('control-center')}
            portfolioId={selectedPortfolio?.id}
          />
        )}

        {activeTab === 'recommendations' && (
          <PortfolioRecommendationsPage
            onBack={() => setActiveTab('control-center')}
            portfolioId={selectedPortfolio?.id}
          />
        )}

        {activeTab === 'details' && (
          <PortfolioDetailsPage
            onBack={() => setActiveTab('control-center')}
            portfolioId={selectedPortfolio?.id}
          />
        )}
      </div>
    </div>
  );
};
