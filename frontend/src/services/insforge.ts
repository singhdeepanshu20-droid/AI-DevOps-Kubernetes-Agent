import { createClient } from '@insforge/sdk';
import { InvestigationHistoryItem, UserSession } from '@/types';

const insforgeUrl = process.env.NEXT_PUBLIC_INSFORGE_URL || 'https://5jfcgcs7.ap-southeast.insforge.app';
const insforgeAnonKey = process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY || 'ik_6ee8f1463d6c3e456c314206bc69e6b6';

export const insforgeClient = createClient({
  baseUrl: insforgeUrl,
  anonKey: insforgeAnonKey,
});

const HISTORY_LOCAL_KEY = 'insforge_k8s_history';
const SESSION_LOCAL_KEY = 'insforge_user_session';

// Auth functions
export async function getInsForgeSession(): Promise<UserSession | null> {
  try {
    const { data } = await insforgeClient.auth.getCurrentUser();
    if (data?.user) {
      return { id: data.user.id, email: data.user.email || 'operator@k8s.local' };
    }
  } catch (e) {
    // Fallback to cached session if offline
  }

  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem(SESSION_LOCAL_KEY);
    if (stored) {
      try { return JSON.parse(stored); } catch (_) {}
    }
  }
  return null;
}

export async function loginInsForge(email: string): Promise<UserSession> {
  const session: UserSession = {
    id: `user-${Date.now()}`,
    email: email || 'sre-engineer@k8s.io'
  };

  try {
    // Attempt sign in with InsForge Auth
    await insforgeClient.auth.signInWithPassword({ email, password: 'password123' });
  } catch (e) {
    // Fallback mock login for local development
  }

  if (typeof window !== 'undefined') {
    localStorage.setItem(SESSION_LOCAL_KEY, JSON.stringify(session));
  }
  return session;
}

export async function logoutInsForge(): Promise<void> {
  try {
    await insforgeClient.auth.signOut();
  } catch (_) {}
  if (typeof window !== 'undefined') {
    localStorage.removeItem(SESSION_LOCAL_KEY);
  }
}

// Investigation History Persistence
export async function saveInvestigationHistory(item: Omit<InvestigationHistoryItem, 'id' | 'timestamp'>): Promise<InvestigationHistoryItem> {
  const newItem: InvestigationHistoryItem = {
    id: `inv-${Date.now()}`,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    ...item
  };

  try {
    // Try InsForge database table insert (takes array of items)
    await insforgeClient.database.from('investigations').insert([newItem]);
  } catch (e) {
    // Graceful fallback to browser storage if table isn't migrated yet
  }

  if (typeof window !== 'undefined') {
    const history = getLocalHistory();
    history.unshift(newItem);
    localStorage.setItem(HISTORY_LOCAL_KEY, JSON.stringify(history.slice(0, 10)));
  }

  return newItem;
}

export async function getInvestigationHistory(): Promise<InvestigationHistoryItem[]> {
  try {
    const { data } = await insforgeClient.database.from('investigations').select('*').order('created_at', { ascending: false }).limit(10);
    if (data && data.length > 0) {
      return data.map((d: any) => ({
        id: d.id || `inv-${Date.now()}`,
        timestamp: d.timestamp || new Date(d.created_at || Date.now()).toLocaleTimeString(),
        root_cause: d.root_cause || 'Unknown',
        namespace: d.namespace || 'default',
        confidence: d.confidence || 80,
        status: d.status || 'success',
        fix: d.fix,
        kubectl_command: d.kubectl_command
      }));
    }
  } catch (e) {
    // Fallback to local storage
  }

  return getLocalHistory();
}

function getLocalHistory(): InvestigationHistoryItem[] {
  if (typeof window === 'undefined') return [];
  const stored = localStorage.getItem(HISTORY_LOCAL_KEY);
  if (!stored) {
    return [
      {
        id: 'inv-sample-1',
        timestamp: '14:22:10',
        root_cause: 'CrashLoopBackOff (DATABASE_URL missing)',
        namespace: 'default',
        confidence: 92,
        status: 'success',
        fix: 'Add missing environment variable',
        kubectl_command: 'kubectl edit deployment payment-service'
      },
      {
        id: 'inv-sample-2',
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
  try {
    return JSON.parse(stored);
  } catch (_) {
    return [];
  }
}
