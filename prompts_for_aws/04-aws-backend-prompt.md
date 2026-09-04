# 04-prompt-aws-dashboard-and-api.md

## Context

The backend can now:

```text
Investigate Kubernetes
        ↓
Collect Evidence
        ↓
AI Reasoning (AWS Bedrock)
        ↓
Root Cause Analysis
        ↓
Suggested Fix
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
AWS Services
(Cognito Auth + DynamoDB History)
```

Goal:

We now want to turn this into a **real application experience**.

Users should be able to:

```text
Click Investigate
        ↓
See live investigation progress
        ↓
Receive diagnosis
        ↓
View investigation history
```

Use AWS for:

```text
Authentication (AWS Cognito)
Investigation History (AWS DynamoDB)
Realtime Updates (WebSockets / SSE)
```

---

## Goal

Build the **Frontend Dashboard + AWS API Integration**.

Implement:

```text
Minimal Dashboard
Authentication (AWS Cognito)
Realtime Investigation Progress
Investigation History (AWS DynamoDB)
Frontend → Backend Integration
```

Keep UI minimal and clean.

Do not overengineer.

---

## Requirements

### 1. Authentication (AWS Cognito)

Add authentication using AWS Cognito (User Pools).

Requirements:

- Login support (Cognito JWT tokens)
- Protected dashboard
- User session handling

Only authenticated users can:

```text
Trigger investigation
View history
See diagnosis
```

Keep auth implementation minimal and clean.

Avoid unnecessary complexity.

---

### 2. Investigation Dashboard

Build a minimal professional dashboard.

UI sections:

### Header

```text
AI Kubernetes Agent
```

### Main CTA

Button:

```text
[ Investigate Cluster ]
```

### Investigation Progress

Show realtime progress.

Example:

```text
✓ Checking Pods
✓ Reading Logs
✓ Analyzing Events
✓ Inspecting Deployments
✓ Checking Networking
✓ AI Reasoning (AWS Bedrock)
✓ Root Cause Found
```

Progress should update while backend investigation runs.

---

### 3. Root Cause Card

Display:

```text
Root Cause
Explanation
Suggested Fix
kubectl Command
Confidence Score
```

Example:

```text
Root Cause:
DATABASE_URL missing

Explanation:
Application failed during startup.

Suggested Fix:
Add missing environment variable.

Command:
kubectl edit deployment payment-service

Confidence:
92%
```

Keep styling clean and beginner friendly.

No complex UI.

---

### 4. Investigation History (AWS DynamoDB)

Save investigations using AWS DynamoDB.

Store in DynamoDB Table `k8s_investigation_history`:

```text
PartitionKey: userId / id
SortKey: timestamp
RootCause
Namespace
Confidence
Status
```

> **First Run Setup Note:** Before running the application for the first time, initialize the AWS DynamoDB table by executing:
> ```bash
> cd backend
> ./venv/bin/python scripts/init_dynamodb.py
> ```
> This script automatically verifies or creates the `k8s_investigation_history` table on AWS DynamoDB.

Display recent investigations.

Example:

```text
Previous Investigations

ImagePullBackOff
CrashLoopBackOff
OOMKilled
```

Simple history table is enough.

No advanced filters.

---

### 5. Frontend API Integration

Frontend should call:

```http
POST /investigate
```

Flow:

```text
User clicks button
        ↓
Frontend API call (with Cognito JWT)
        ↓
Backend investigation
        ↓
Realtime progress updates
        ↓
Diagnosis returned (from AWS Bedrock)
        ↓
UI updates & DynamoDB history saved
```

Handle:

```text
Loading state
API failures
Empty response
Timeouts
```

---

## Frontend Expectations

Minimal professional UI.

Example layout:

```text
------------------------------------

AI Kubernetes Agent

[ Investigate Cluster ]

Investigation Status

✓ Checking Pods
✓ Reading Logs
✓ AI Reasoning (AWS Bedrock)

Diagnosis

Root Cause:
CrashLoopBackOff

Fix:
Update env variable

Confidence:
92%

Recent Investigations (DynamoDB)
----------------------------------
ImagePullBackOff
OOMKilled

------------------------------------
```

Simple.

Professional.

Easy to explain in a YouTube tutorial.

---

## Constraints

DO NOT change working backend investigation logic.

DO NOT change AI reasoning flow.

DO NOT overengineer UI.

DO NOT add charts.

DO NOT add complex state management.

Use AWS only for:

```text
Authentication (Cognito)
AI Model Hosting (Bedrock)
Investigation history (DynamoDB / RDS)
```

FastAPI must remain the orchestrator.

DO NOT BREAK EXISTING CODE.

Only extend functionality.

---

## Expected Result

Users should now be able to:

```text
Login (Cognito)
        ↓
Open Dashboard
        ↓
Click Investigate
        ↓
Watch realtime progress
        ↓
Receive diagnosis (Bedrock)
        ↓
See investigation history (DynamoDB)
```

The system should now feel like:

> A real AWS-powered AI Kubernetes troubleshooting product.
