# 05-prompt-integration-testing-deployment.md

## Context

The application is now complete.

Users can:

```text
Login (AWS Cognito)
        ↓
Click "Investigate Cluster"
        ↓
Backend investigates Kubernetes
        ↓
AI reasons about failures (AWS Bedrock)
        ↓
Root cause generated
        ↓
Suggested fix shown
        ↓
Investigation history saved (AWS DynamoDB)
```

Architecture:

```text
Frontend
    ↓
FastAPI Backend (Orchestrator)
    ↓
Kubernetes Investigation Layer
    ↓
AI Kubernetes Agent
    ↓
LLM Reasoning
(AWS Bedrock via boto3)
    ↓
Root Cause + Suggested Fix
    ↓
AWS Infrastructure
(Cognito + DynamoDB + IAM)
    ↓
Frontend Diagnosis
```

Goal:

We now want to:

1. Integrate everything end-to-end
2. Test real Kubernetes failures
3. Improve reliability

This step should make the system feel like a **real product**.

---

## Goal

Implement:

```text
End-to-End Integration
Error Handling
Loading States
Real Kubernetes Failure Testing
```

Keep implementation beginner friendly.

Do not overengineer.

---

## Requirements

### 1. End-to-End Integration

Validate the full flow.

Expected workflow:

```text
User clicks Investigate
        ↓
Frontend sends API request
        ↓
FastAPI orchestrates investigation
        ↓
Kubernetes evidence collected
        ↓
AI reasoning triggered (AWS Bedrock)
        ↓
Root cause generated
        ↓
Suggested fix returned
        ↓
History saved (DynamoDB)
        ↓
Realtime UI updated
        ↓
User sees diagnosis
```

Ensure all components work together.

Fix integration issues if needed.

---

### 2. Improve Reliability

Add proper error handling.

Handle:

```text
kubectl failures
Cluster unreachable
Missing kubeconfig
AWS Bedrock throttles / failures
AWS IAM authorization issues
API timeout
No unhealthy resources found
Authentication issues
```

Show beginner-friendly error messages.

Example:

```text
Unable to connect to Kubernetes cluster or AWS Bedrock.

Please verify:
- kubeconfig path
- cluster access
- AWS credentials / IAM policies
- kubectl permissions
```

Avoid ugly stack traces in UI.

---

### 3. Loading & Empty States

Improve UX.

When investigation starts:

Show:

```text
Investigating Kubernetes Cluster...
```

During investigation:

```text
✓ Checking Pods
✓ Reading Logs
✓ Analyzing Events
✓ Inspecting Deployments
✓ Checking Networking
✓ AI Reasoning (AWS Bedrock)
```

If no issue found:

```text
No critical Kubernetes issues detected.
Cluster appears healthy.
```

---

### 4. Test Real Kubernetes Failures

Create intentional Kubernetes failure scenarios for testing.

Test these scenarios:

### Scenario 1 — CrashLoopBackOff

Example:

```text
Missing environment variable
```

Expected:

```text
Root Cause:
Missing env variable

Suggested Fix:
Add missing secret/configmap value
```

---

### Scenario 2 — ImagePullBackOff

Example:

```text
Wrong image tag
```

Expected:

```text
Root Cause:
Invalid image tag

Fix:
Update deployment image
```

---

### Scenario 3 — OOMKilled

Example:

```text
Low memory limits
```

Expected:

```text
Root Cause:
Container exceeded memory limit

Fix:
Increase memory requests/limits
```

---

### Scenario 4 — Service Selector Mismatch

Example:

```text
Wrong labels
```

Expected:

```text
Root Cause:
Service selector does not match pod labels

Fix:
Update service selector
```

Validate that the AI agent can troubleshoot real Kubernetes problems.

---

Important:

Make sure to display all the Kubernetes clusters on my local machine part of the kubeconfig file. User can click on the cluster and that cluster investigation is performed.
