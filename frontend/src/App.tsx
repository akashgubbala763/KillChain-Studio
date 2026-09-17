import React, { useEffect, useState } from 'react';
import { 
  Shield, 
  Activity, 
  Database, 
  Server, 
  Layers, 
  CheckCircle2, 
  AlertTriangle,
  RefreshCw,
  Cpu,
  Terminal,
  Clock
} from 'lucide-react';
import { systemApi } from './services/api';
import { HealthStatus, DbHealthStatus } from './types';

export const App: React.FC = () => {
  const [backendHealth, setBackendHealth] = useState<HealthStatus | null>(null);
  const [dbHealth, setDbHealth] = useState<DbHealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastCheck, setLastCheck] = useState<string>('');

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const [backendRes, dbRes] = await Promise.all([
        systemApi.checkHealth(),
        systemApi.checkDbHealth(),
      ]);
      setBackendHealth(backendRes);
      setDbHealth(dbRes);
      setLastCheck(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend server');
      setLastCheck(new Date().toLocaleTimeString());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-[#0a0d14]/90 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center glow-blue shadow-lg shadow-sky-500/20">
            <Shield className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg text-white tracking-wide">SOC Platform</h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono">
                Phase 1 Active
              </span>
            </div>
            <p className="text-xs text-slate-400">Intelligent Network Security & Attack Reconstruction</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs text-slate-400 font-mono bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
            <Clock className="h-3.5 w-3.5 text-slate-400" />
            <span>Updated: {lastCheck || 'Connecting...'}</span>
          </div>
          <button
            onClick={fetchHealth}
            disabled={loading}
            className="flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition border border-slate-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </header>

      {/* Main Content Dashboard */}
      <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full space-y-6">
        {/* Welcome & Platform Overview Banner */}
        <div className="relative overflow-hidden rounded-2xl border border-sky-500/20 bg-gradient-to-r from-sky-950/40 via-slate-900/60 to-indigo-950/40 p-6 md:p-8">
          <div className="relative z-10 space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
              <Activity className="h-3.5 w-3.5" />
              SYSTEM FOUNDATION ESTABLISHED
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
              Intelligent Network Security Monitoring & Attack Reconstruction
            </h2>
            <p className="text-slate-300 text-sm max-w-3xl leading-relaxed">
              Full-stack cybersecurity operations platform uniting multi-signal detection (Deterministic Rules, Supervised Machine Learning, and Isolation Forest Anomalies), dynamic behavioral baseline profiling ($Z$-scores), and temporal attack lifecycle reconstruction.
            </p>
          </div>
        </div>

        {/* Connectivity & Health Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Backend Health Card */}
          <div className="glass-panel rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  <Server className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">FastAPI Core Service</h3>
                  <p className="text-xs text-slate-400">Backend API Engine</p>
                </div>
              </div>
              {backendHealth ? (
                <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
                  <CheckCircle2 className="h-3.5 w-3.5" /> Online
                </span>
              ) : (
                <span className="flex items-center gap-1.5 text-xs font-semibold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/20">
                  <AlertTriangle className="h-3.5 w-3.5" /> Checking
                </span>
              )}
            </div>

            <div className="border-t border-slate-800/80 pt-3 space-y-2 text-xs font-mono text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-500">Service:</span>
                <span className="text-slate-200">{backendHealth?.service || 'Connecting...'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Version:</span>
                <span className="text-sky-400">{backendHealth?.version || '1.0.0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Environment:</span>
                <span className="text-slate-200">{backendHealth?.environment || 'development'}</span>
              </div>
            </div>
          </div>

          {/* Database Health Card */}
          <div className="glass-panel rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <Database className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Storage & Forensic DB</h3>
                  <p className="text-xs text-slate-400">SQLAlchemy 2.0 Engine</p>
                </div>
              </div>
              {dbHealth?.status === 'connected' ? (
                <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
                  <CheckCircle2 className="h-3.5 w-3.5" /> Connected
                </span>
              ) : (
                <span className="flex items-center gap-1.5 text-xs font-semibold text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/20">
                  <AlertTriangle className="h-3.5 w-3.5" /> Initializing
                </span>
              )}
            </div>

            <div className="border-t border-slate-800/80 pt-3 space-y-2 text-xs font-mono text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-500">Engine Type:</span>
                <span className="text-emerald-400 uppercase">{dbHealth?.database_type || 'POSTGRESQL / SQLITE'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Status:</span>
                <span className="text-slate-200">{dbHealth?.status || 'Querying...'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Pooling:</span>
                <span className="text-slate-200">Async Contextual</span>
              </div>
            </div>
          </div>

          {/* Multi-Signal Detection Architecture Card */}
          <div className="glass-panel rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Cpu className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Detection Pipeline</h3>
                  <p className="text-xs text-slate-400">Multi-Signal Intelligence</p>
                </div>
              </div>
              <span className="flex items-center gap-1.5 text-xs font-semibold text-sky-400 bg-sky-500/10 px-2.5 py-1 rounded-full border border-sky-500/20">
                <Layers className="h-3.5 w-3.5" /> 3 Signals
              </span>
            </div>

            <div className="border-t border-slate-800/80 pt-3 space-y-2 text-xs text-slate-300">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Deterministic Rules:</span>
                <span className="text-emerald-400 font-mono">6 Core Rules</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">ML Classifier:</span>
                <span className="text-sky-400 font-mono">Random Forest</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Anomaly Detector:</span>
                <span className="text-indigo-400 font-mono">Isolation Forest</span>
              </div>
            </div>
          </div>
        </div>

        {/* System Architecture Roadmap Progress */}
        <div className="glass-panel rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Terminal className="h-4 w-4 text-sky-400" />
                Phase Roadmap Execution Progress
              </h3>
              <p className="text-xs text-slate-400">
                Tracking full platform lifecycle from architectural design to interactive attack reconstruction
              </p>
            </div>
            <span className="text-xs font-mono text-sky-400 bg-sky-500/10 px-3 py-1 rounded-lg border border-sky-500/20">
              Phase 1 / 14 Completed
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-900/90 border border-emerald-500/40 space-y-1">
              <div className="flex items-center justify-between font-semibold text-emerald-400">
                <span>Phase 0: Specifications</span>
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <p className="text-slate-400">Comprehensive requirements, architecture, schemas & ML designs.</p>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/90 border border-sky-500/40 space-y-1 glow-blue">
              <div className="flex items-center justify-between font-semibold text-sky-400">
                <span>Phase 1: Foundation</span>
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <p className="text-slate-400">FastAPI async core, React/Vite UI, Docker configurations & health checks.</p>
            </div>

            <div className="p-3 rounded-lg bg-slate-900/40 border border-slate-800 space-y-1 opacity-70">
              <div className="flex items-center justify-between font-semibold text-slate-300">
                <span>Phase 2: Database & Auth</span>
                <span className="text-slate-500 font-mono">NEXT</span>
              </div>
              <p className="text-slate-500">PostgreSQL models, Alembic migrations, JWT tokens, RBAC roles & seed data.</p>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/30 flex items-center gap-3 text-red-300 text-xs">
            <AlertTriangle className="h-5 w-5 text-red-400 flex-shrink-0" />
            <div>
              <p className="font-semibold text-red-200">Backend Communication Notice</p>
              <p>{error}</p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#0a0d14]/90 px-6 py-4 text-center text-xs text-slate-500">
        Intelligent Network Security Monitoring & Attack Reconstruction Platform &bull; Major Final-Year Engineering Project
      </footer>
    </div>
  );
};

export default App;
