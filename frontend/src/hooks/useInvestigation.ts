import { useState, useEffect, useCallback, useRef } from 'react';
import { runInvestigation } from '@/services/api';
import { Diagnosis, InvestigationHistoryItem, InvestigationResult } from '@/types';
import { fetchAWSDynamoDBHistory } from '@/services/aws';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const PROGRESS_STEPS = [
  'Checking Pods',
  'Reading Logs',
  'Analyzing Events',
  'Inspecting Deployments',
  'Checking Networking',
  'AI Reasoning (AWS Bedrock)',
  'Root Cause Found'
];

export function useInvestigation() {
  const [loading, setLoading] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(-1);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<InvestigationHistoryItem[]>([]);
  const stepTimerRef = useRef<NodeJS.Timeout | null>(null);

  const refreshHistory = useCallback(async () => {
    const items = await fetchAWSDynamoDBHistory();
    setHistory(items);
  }, []);

  useEffect(() => {
    refreshHistory();
  }, [refreshHistory]);

  const startStepProgressSimulation = () => {
    let step = 0;
    setCurrentStepIndex(0);

    if (stepTimerRef.current) {
      clearInterval(stepTimerRef.current);
    }

    stepTimerRef.current = setInterval(() => {
      step += 1;
      if (step <= 5) {
        setCurrentStepIndex(step);
      } else {
        if (stepTimerRef.current) clearInterval(stepTimerRef.current);
      }
    }, 700);
  };

  const stopStepProgressSimulation = () => {
    if (stepTimerRef.current) {
      clearInterval(stepTimerRef.current);
      stepTimerRef.current = null;
    }
  };

  const investigate = async (namespace: string = 'default', clusterContext?: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    startStepProgressSimulation();

    const queryParams = new URLSearchParams({ namespace });
    if (clusterContext) {
      queryParams.append('cluster_context', clusterContext);
    }

    // Use SSE (Server-Sent Events) for live streaming progress updates
    if (typeof window !== 'undefined' && 'EventSource' in window) {
      try {
        const streamUrl = `${API_BASE_URL}/investigate/stream?${queryParams.toString()}`;
        const eventSource = new EventSource(streamUrl);

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (typeof data.step === 'number' && data.step >= 0) {
              setCurrentStepIndex(data.step);
            }
            if (data.status === 'error') {
              stopStepProgressSimulation();
              setCurrentStepIndex(-1);
              setError(data.error || 'Unable to connect to Kubernetes cluster or AWS Bedrock.');
              if (data.result) {
                setResult(data.result);
              }
              setLoading(false);
              eventSource.close();
              return;
            }
            if (data.status === 'completed' && data.result) {
              stopStepProgressSimulation();
              setCurrentStepIndex(6);
              if (data.result.status === 'error') {
                setError(data.result.message || 'Unable to connect to Kubernetes cluster or AWS Bedrock.');
              }
              setResult(data.result);
              setLoading(false);
              eventSource.close();
              refreshHistory();
            }
          } catch (e) {
            console.error('SSE JSON parse error:', e);
          }
        };

        eventSource.onerror = async (err) => {
          console.warn('SSE stream connection dropped, falling back to REST API...', err);
          eventSource.close();
          // Fallback to standard POST /investigate
          try {
            const res = await runInvestigation(namespace, clusterContext);
            stopStepProgressSimulation();
            setCurrentStepIndex(6);
            if (res.status === 'error') {
              setError(res.message || 'Unable to connect to Kubernetes cluster or AWS Bedrock.');
            }
            setResult(res);
            await refreshHistory();
          } catch (apiErr: any) {
            stopStepProgressSimulation();
            setCurrentStepIndex(-1);
            const msg = apiErr?.response?.data?.message || apiErr?.message || 'Backend server is offline or unreachable on port 8000.';
            setError(msg);
          } finally {
            setLoading(false);
          }
        };
        return;
      } catch (sseErr) {
        console.warn('SSE initialization failed, using REST fallback', sseErr);
      }
    }

    // Standard POST fallback
    try {
      const res = await runInvestigation(namespace, clusterContext);
      stopStepProgressSimulation();
      setCurrentStepIndex(6);
      if (res.status === 'error') {
        setError(res.message || 'Unable to connect to Kubernetes cluster or AWS Bedrock.');
      }
      setResult(res);
      await refreshHistory();
    } catch (err: any) {
      stopStepProgressSimulation();
      setCurrentStepIndex(-1);
      const msg = err?.response?.data?.message || err?.message || 'Backend server is offline or unreachable on port 8000.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return {
    investigate,
    loading,
    currentStepIndex,
    progressSteps: PROGRESS_STEPS,
    result,
    error,
    history,
    refreshHistory
  };
}
