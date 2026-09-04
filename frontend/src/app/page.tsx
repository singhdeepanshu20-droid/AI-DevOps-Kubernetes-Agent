'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { ProgressCard } from '@/components/ProgressCard';
import { RootCauseCard } from '@/components/RootCauseCard';
import { HistoryTable } from '@/components/HistoryTable';
import { AuthModal } from '@/components/AuthModal';
import { useInvestigation } from '@/hooks/useInvestigation';
import { getAWSSession, logoutAWSCognito, loginAWSCognito } from '@/services/aws';
import { getClusters } from '@/services/api';
import { Diagnosis, UserSession } from '@/types';
import { Play, Activity, AlertCircle, RefreshCw, Server, Sparkles, CheckCircle2, Cloud, Cpu } from 'lucide-react';

const DEFAULT_CLUSTERS = [
  'kind-kubernetes-demo-cluster',
  'minikube',
  'arn:aws:eks:ap-southeast-2:858230644504:cluster/eks-cluster'
];

export default function Home() {
  const [user, setUser] = useState<UserSession | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [namespace, setNamespace] = useState('default');
  const [clusters, setClusters] = useState<string[]>(DEFAULT_CLUSTERS);
  const [selectedCluster, setSelectedCluster] = useState<string>('kind-kubernetes-demo-cluster');

  const {
    investigate,
    loading,
    currentStepIndex,
    progressSteps,
    result,
    error,
    history
  } = useInvestigation();

  useEffect(() => {
    getAWSSession().then((session) => {
      if (!session) {
        loginAWSCognito('sre-engineer@aws.cloud').then((defaultSession) => {
          setUser(defaultSession);
        });
      } else {
        setUser(session);
      }
    });

    getClusters().then((res) => {
      if (res.clusters && res.clusters.length > 0) {
        setClusters(res.clusters);
        setSelectedCluster(res.current_context || res.clusters[0]);
      }
    });
  }, []);

  const handleLogout = async () => {
    await logoutAWSCognito();
    setUser(null);
  };

  const handleStartInvestigation = () => {
    if (!user) {
      setAuthModalOpen(true);
      return;
    }
    investigate(namespace, selectedCluster || undefined);
  };

  const diagnosis = result?.diagnosis && typeof result.diagnosis === 'object'
    ? (result.diagnosis as Diagnosis)
    : null;

  return (
    <div className="min-h-screen text-slate-100 flex flex-col font-sans selection:bg-amber-500 selection:text-white relative overflow-x-hidden">
      {/* Header with AWS Cognito Auth Status */}
      <Header
        user={user}
        onOpenAuth={() => setAuthModalOpen(true)}
        onLogout={handleLogout}
      />

      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-12 flex flex-col items-center text-center space-y-12 z-10">
        {/* Hero Section */}
        <div className="space-y-5 max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold tracking-wide uppercase shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            <span>AWS Bedrock Automated SRE Agent</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white leading-tight">
            AI Kubernetes Agent <span className="bg-gradient-to-r from-amber-400 via-orange-400 to-amber-500 bg-clip-text text-transparent">(AWS Native)</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 max-w-xl mx-auto leading-relaxed">
            Realtime evidence collection, AWS Bedrock LLM reasoning, root cause analysis & instant fixes.
          </p>
        </div>

        {/* Cluster Selection Tiles Section */}
        <div className="w-full space-y-4 max-w-4xl">
          <div className="flex items-center justify-between px-1">
            <label className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center space-x-2">
              <Server className="w-4 h-4 text-amber-400" />
              <span>Select Kubernetes Cluster Context</span>
            </label>
            <span className="text-xs text-slate-400 font-mono">
              {clusters.length} Cluster{clusters.length > 1 ? 's' : ''} Configured
            </span>
          </div>

          {/* Cluster Tiles Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
            {clusters.map((cluster) => {
              const isSelected = selectedCluster === cluster;
              const isEKS = cluster.includes('eks') || cluster.includes('arn:aws');
              const isMinikube = cluster.includes('minikube');
              const isKind = cluster.includes('kind');

              let badgeLabel = 'Local Cluster';
              let icon = <Server className="w-5 h-5 text-amber-400" />;

              if (isEKS) {
                badgeLabel = 'AWS EKS Cloud';
                icon = <Cloud className="w-5 h-5 text-orange-400" />;
              } else if (isKind) {
                badgeLabel = 'Local Kind';
                icon = <Cpu className="w-5 h-5 text-amber-400" />;
              } else if (isMinikube) {
                badgeLabel = 'Local Minikube';
                icon = <Activity className="w-5 h-5 text-blue-400" />;
              }

              return (
                <div
                  key={cluster}
                  onClick={() => setSelectedCluster(cluster)}
                  className={`cursor-pointer rounded-3xl p-5 transition-all duration-300 flex flex-col justify-between space-y-4 text-left border ${
                    isSelected
                      ? 'bg-slate-900 border-amber-500/90 shadow-2xl shadow-amber-500/15 ring-2 ring-amber-500/30 scale-[1.02]'
                      : 'bg-slate-900/50 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/80 hover:scale-[1.01]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-2xl bg-slate-950/80 border border-slate-800/80">
                      {icon}
                    </div>
                    {isSelected ? (
                      <span className="inline-flex items-center space-x-1 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[11px] font-bold shadow-sm">
                        <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
                        <span>Active Target</span>
                      </span>
                    ) : (
                      <span className="px-3 py-1 rounded-full bg-slate-950/80 border border-slate-800 text-slate-400 text-[11px] font-mono">
                        {badgeLabel}
                      </span>
                    )}
                  </div>

                  <div>
                    <h4 className="font-bold text-sm text-slate-100 font-mono break-all leading-tight" title={cluster}>
                      {cluster}
                    </h4>
                    <p className="text-[11px] text-slate-400 font-mono mt-1.5">
                      {isEKS ? 'Managed AWS EKS Cluster' : 'Local Development Cluster'}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Namespace & CTA Card */}
        <div className="glass-card p-6 rounded-3xl max-w-4xl w-full flex flex-col md:flex-row items-center justify-between gap-5">
          <div className="text-left w-full md:w-2/3 space-y-1.5">
            <label className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">Target Kubernetes Namespace</label>
            <input
              type="text"
              value={namespace}
              onChange={(e) => setNamespace(e.target.value)}
              placeholder="e.g. default, kube-system"
              className="bg-slate-950/90 border border-slate-700/80 text-slate-200 text-sm rounded-2xl px-4 py-3 font-mono w-full focus:outline-none focus:border-amber-500 shadow-inner transition-all hover:border-slate-600"
            />
          </div>

          <div className="w-full md:w-auto flex items-end pt-2 md:pt-5">
            <button
              onClick={handleStartInvestigation}
              disabled={loading}
              className="w-full md:w-auto inline-flex items-center justify-center space-x-2.5 px-8 py-3.5 text-base font-bold text-white rounded-2xl btn-gradient disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 shadow-xl shadow-amber-600/20"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin text-white" />
                  <span>Investigating...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 fill-current text-white" />
                  <span>Investigate Selected Cluster</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Beginner Friendly Error State */}
        {error && (
          <div className="p-6 max-w-3xl w-full bg-red-950/70 border border-red-800/80 text-red-200 rounded-3xl text-sm text-left space-y-4 shadow-2xl backdrop-blur-md">
            <div className="flex items-center space-x-3 text-red-400">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <h4 className="font-bold text-base">Unable to connect to Kubernetes cluster or AWS Bedrock</h4>
            </div>
            <p className="text-xs text-red-300 leading-relaxed whitespace-pre-line">{error}</p>
            <div className="bg-red-900/40 border border-red-800/50 p-4 rounded-2xl text-xs space-y-1.5 font-mono">
              <span className="font-semibold text-red-200 block mb-1">Please verify:</span>
              <p>• kubeconfig path & cluster connectivity</p>
              <p>• selected cluster tile context</p>
              <p>• AWS credentials / IAM policies (bedrock:InvokeModel)</p>
              <p>• kubectl permissions for target namespace</p>
            </div>
          </div>
        )}

        {/* Realtime Progress Steps Card */}
        {loading && (
          <ProgressCard steps={progressSteps} currentIndex={currentStepIndex} />
        )}

        {/* Diagnosis Result Card */}
        {diagnosis && !loading && (
          <RootCauseCard diagnosis={diagnosis} />
        )}

        {/* Previous Investigations Table (AWS DynamoDB) */}
        <HistoryTable items={history} />
      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={(session) => setUser(session)}
      />

      <footer className="border-t border-slate-900/80 py-8 text-center text-xs text-slate-500 font-mono backdrop-blur-md">
        AI Kubernetes Agent • AWS Bedrock + AWS Cognito + AWS DynamoDB • 2026
      </footer>
    </div>
  );
}
