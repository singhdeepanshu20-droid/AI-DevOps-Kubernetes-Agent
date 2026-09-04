export interface HealthStatus {
  status: string;
  service: string;
}

export interface Diagnosis {
  root_cause: string;
  explanation: string;
  fix: string;
  kubectl_command: string;
  prevention?: string;
  confidence: number;
}

export interface InvestigationResult {
  status: string;
  message?: string;
  error?: string;
  investigation?: Record<string, any>;
  diagnosis?: Diagnosis;
}

export interface ClusterListResponse {
  clusters: string[];
  current_context: string | null;
}

export interface InvestigationHistoryItem {
  id?: string;
  timestamp: string;
  root_cause: string;
  namespace: string;
  confidence: number;
  status: string;
  fix?: string;
  kubectl_command?: string;
}

export interface UserSession {
  email: string;
  id: string;
}
