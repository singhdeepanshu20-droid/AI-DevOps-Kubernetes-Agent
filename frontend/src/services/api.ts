import axios from 'axios';
import { HealthStatus, InvestigationResult, ClusterListResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000,
});

export const getHealth = async (): Promise<HealthStatus> => {
  const response = await apiClient.get<HealthStatus>('/health');
  return response.data;
};

export const getClusters = async (): Promise<ClusterListResponse> => {
  try {
    const response = await apiClient.get<ClusterListResponse>('/clusters');
    if (response.data && response.data.clusters && response.data.clusters.length > 0) {
      return response.data;
    }
  } catch (error) {
    console.warn('Failed to fetch Kubernetes cluster contexts from backend API:', error);
  }

  // Fallback to local clusters list if backend endpoint is unreachable or initializing
  return {
    clusters: [
      'kind-kubernetes-demo-cluster',
      'minikube',
      'arn:aws:eks:ap-southeast-2:858230644504:cluster/eks-cluster'
    ],
    current_context: 'kind-kubernetes-demo-cluster'
  };
};

export const runInvestigation = async (
  namespace?: string,
  clusterContext?: string
): Promise<InvestigationResult> => {
  const response = await apiClient.post<InvestigationResult>('/investigate', {
    namespace: namespace || 'default',
    cluster_context: clusterContext || undefined
  });
  return response.data;
};
