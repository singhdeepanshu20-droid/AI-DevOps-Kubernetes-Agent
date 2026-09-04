import { InvestigationHistoryItem, UserSession } from '@/types';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const SESSION_LOCAL_KEY = 'aws_user_session';

export async function getAWSSession(): Promise<UserSession | null> {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem(SESSION_LOCAL_KEY);
    if (stored) {
      try { return JSON.parse(stored); } catch (_) {}
    }
  }
  return null;
}

export async function loginAWSCognito(email: string): Promise<UserSession> {
  const session: UserSession = {
    id: `cognito-user-${Date.now()}`,
    email: email || 'sre-engineer@aws.cloud'
  };

  if (typeof window !== 'undefined') {
    localStorage.setItem(SESSION_LOCAL_KEY, JSON.stringify(session));
  }
  return session;
}

export async function logoutAWSCognito(): Promise<void> {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(SESSION_LOCAL_KEY);
  }
}

export async function fetchAWSDynamoDBHistory(): Promise<InvestigationHistoryItem[]> {
  try {
    const res = await axios.get<InvestigationHistoryItem[]>(`${API_BASE_URL}/history`);
    return res.data;
  } catch (e) {
    return [
      {
        id: 'inv-sample-aws-1',
        timestamp: '14:22:10',
        root_cause: 'CrashLoopBackOff (DATABASE_URL missing)',
        namespace: 'default',
        confidence: 92,
        status: 'success',
        fix: 'Add missing environment variable',
        kubectl_command: 'kubectl edit deployment payment-service'
      },
      {
        id: 'inv-sample-aws-2',
        timestamp: '11:05:40',
        root_cause: 'ImagePullBackOff (Invalid tag)',
        namespace: 'kube-system',
        confidence: 90,
        status: 'success',
        fix: 'Fix image tag in manifest',
        kubectl_command: 'kubectl set image deployment/web nginx=nginx:1.25'
      }
    ];
  }
}
