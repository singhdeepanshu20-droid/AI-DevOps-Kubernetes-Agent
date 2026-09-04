# 🚀 AI DevOps Kubernetes Troubleshooting Agent (AWS Bedrock + SRE AI Engine)

## 🎯 Goal

Build an AI-powered Kubernetes troubleshooting platform that can:

- 🔎 Automatically investigate Kubernetes cluster failures in under 8 seconds
- 📋 Analyze container logs, warning events, pod health, and deployment states
- 🤖 Identify exact root causes using AWS Bedrock AI (`qwen.qwen3-coder-next`)
- 💡 Recommend instant, copyable `kubectl` fix commands
- ⚡ Stream real-time progress updates via Server-Sent Events (SSE)
- 💾 Store historical investigation reports in AWS DynamoDB for audit trailing
- ☁️ Deploy seamlessly on local development environments or AWS Cloud

---

# 🏛️ High Level Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                     │
│                                                            │
│  Pods | Deployments | Services | Events | Logs            │
│  Target Clusters: Kind | Minikube | AWS EKS               │
│                                                            │
│  This is where failures happen and evidence exists         │
└────────────────────────────────────────────────────────────┘
                              │
                              │ kubectl CLI / Kubernetes API
                              ▼
┌────────────────────────────────────────────────────────────┐
│                  Investigation Layer                      │
│                                                            │
│ Responsibility:                                            │
│ - Connect to target Kubernetes cluster                     │
│ - Collect troubleshooting signals (non-blocking 8s timeout)│
│ - Gather diagnostic evidence payload                       │
│                                                            │
│ Components:                                                │
│                                                            │
│  1. Pod Inspector                                          │
│     - Check pod health & restart counts                    │
│     - Detect CrashLoopBackOff & Error states               │
│                                                            │
│  2. Logs Collector                                         │
│     - Read container stdout & stderr logs                  │
│     - Capture application stack traces                     │
│                                                            │
│  3. Events Analyzer                                        │
│     - Read Kubernetes warning events                       │
│     - Detect scheduling, volume, & image pull failures     │
│                                                            │
│  4. Deployment Inspector                                   │
│     - Inspect deployment rollout health                    │
│     - Verify replica availability & spec integrity         │
│                                                            │
│  5. Network Inspector                                      │
│     - Check services & active endpoints                    │
│     - Validate label selectors & DNS connectivity          │
└────────────────────────────────────────────────────────────┘
                              │
                              │ Structured Diagnostic Evidence Payload
                              ▼
┌────────────────────────────────────────────────────────────┐
│         AI Kubernetes Agent (AWS Bedrock Runtime)          │
│                                                            │
│ Responsibility:                                            │
│ - Understand Kubernetes failure patterns                   │
│ - Correlate logs + events + pod state                      │
│ - Identify root cause using SRE domain knowledge           │
│ - Recommend copyable kubectl fixes & prevention steps      │
│                                                            │
│ Components:                                                │
│                                                            │
│  1. Diagnostic Payload Synthesizer                         │
│     - Format evidence into structured SRE AI prompt        │
│                                                            │
│  2. LLM Reasoning Layer                                    │
│     - AWS Bedrock Converse API integration                 │
│     - SRE AI Model (qwen.qwen3-coder-next)                 │
│                                                            │
│  3. Root Cause Analyzer                                    │
│     - Isolate primary failure & multi-signal correlations  │
│                                                            │
│  4. Fix Recommendation Engine                              │
│     - Generate copyable kubectl fix commands               │
│     - Recommend YAML/configuration corrections             │
│                                                            │
│  5. Confidence Scoring                                     │
│     - Calculate percentage diagnostic confidence           │
└────────────────────────────────────────────────────────────┘
                              │
                              │ Structured SRE Diagnosis JSON
                              ▼
┌────────────────────────────────────────────────────────────┐
│              Core API Backend (FastAPI Server)             │
│                                                            │
│ Responsibility:                                            │
│ - SRE Authentication (AWS Cognito / Local JWT mock)        │
│ - API Orchestration (POST /investigate endpoint)           │
│ - Realtime SSE progress streaming                          │
│ - Audit persistence (AWS DynamoDB Table)                   │
│                                                            │
│ Components:                                                │
│                                                            │
│  1. Identity & Security Layer                              │
│     - AWS Cognito User Pool / JWT validation               │
│                                                            │
│  2. API Orchestration Engine                               │
│     - Coordinate inspector, AI reasoning, & persistence    │
│                                                            │
│  3. Real-time Progress Streamer                            │
│     - Server-Sent Events (SSE) progress push             │
│                                                            │
│  4. Audit History Storage                                  │
│     - Save past reports to AWS DynamoDB                    │
└────────────────────────────────────────────────────────────┘
                              │
                              │ SSE Stream Updates & Final API Response
                              ▼
┌────────────────────────────────────────────────────────────┐
│             Frontend Dashboard (Next.js 14 UI)             │
│                                                            │
│ Responsibility:                                            │
│ - Select target cluster card & trigger investigation       │
│ - Display real-time step progress bar                      │
│ - Render root cause warning banner                         │
│ - Provide copyable kubectl fix commands                    │
│ - View audit history logs                                  │
│                                                            │
│ UI Example:                                                │
│  ✓ Incident: Payment Service Failure (CrashLoopBackOff)    │
│  ✓ Live Steps: Pods Checked ➔ Logs Read ➔ AI Analyzed      │
│  ✓ Diagnosis: Missing DATABASE_URL env var                 │
│  ✓ Copyable Fix: kubectl set env deployment/...            │
└────────────────────────────────────────────────────────────┘
                              │
                              │ Deployment Targets
                              ▼
┌────────────────────────────────────────────────────────────┐
│                Deployment & Infrastructure                 │
│                                                            │
│ Responsibility:                                            │
│ - Containerize app services                                │
│ - Host backend API & frontend UI                           │
│                                                            │
│ Output / Environment Options:                              │
│  - Local Dev: Docker Compose (docker compose up)           │
│  - AWS Cloud: App Runner / ECS (Backend) + Amplify         │
└────────────────────────────────────────────────────────────┘
```

---

# 🔄 End-to-End Workflow

```text
User clicks "Run Investigation" on Cluster Card
                │
                ▼
Next.js 14 Frontend sends API Request (with Bearer JWT Token)
                │
                ▼
FastAPI Backend (Orchestration Layer)
                │
                ├── Authenticate User (AWS Cognito / Local Mock)
                │
                ▼
Kubernetes Investigation Layer
                │
                ├── 1. Pod Inspector (Check Pod status & restart counts)
                ├── 2. Logs Collector (Read container stdout/stderr)
                ├── 3. Events Analyzer (Scan K8s warning events)
                ├── 4. Deployment Inspector (Verify rollout health)
                └── 5. Network Inspector (Check services & selectors)
                │
                ▼
Diagnostic Evidence Payload Generated
                │
                ▼
AI Kubernetes Agent (AWS Bedrock Runtime)
                │
                ▼
LLM Reasoning & Synthesis (Qwen3 Coder Next via Boto3 Converse)
                │
                ▼
Root Cause Analysis & Structured SRE Fix Generated
                │
                ├── Save Audit Record (AWS DynamoDB Table)
                │
                ├── Stream Realtime Progress Updates (SSE Stream)
                │
                ▼
Frontend Receives SSE Result Stream
                │
                ▼
User Sees Red/Amber Diagnosis Banner & Copyable Fix Command
```

---

# 🚨 Example Failure Flow

```text
Issue:
Payment service unavailable / Pod failing in production

Agent Investigation:
✓ Pod Status Checked (Detected CrashLoopBackOff)
✓ Logs Collected ("Error: DATABASE_URL environment variable missing")
✓ Warning Events Analyzed (Back-off 5m0s restarting failed container)

Detected Problem:
CrashLoopBackOff

Root Cause:
DATABASE_URL environment variable missing or empty in pod deployment manifest

Confidence:
96%

Suggested Fix:
kubectl set env deployment/payment-service DATABASE_URL=postgres://db.internal:5432/paymentdb

Prevention:
Add mandatory env validation in container entrypoint and update helm chart values
```

---

## 🛠️ Supported Kubernetes Problems

- 🔴 **CrashLoopBackOff** (Application crashes on startup / missing env vars)
- 📦 **ImagePullBackOff / ErrImagePull** (Invalid image tag or missing registry credentials)
- 💥 **OOMKilled** (Container exceeding memory resource limits)
- ⏳ **Pending Pods** (Insufficient CPU/Memory node capacity or unschedulable constraints)
- 🛑 **Readiness / Liveness Probe Failures** (Healthcheck endpoint timeout or failure)
- 🔀 **Service Selector Mismatch** (Service pointing to invalid pod labels)
- 🌐 **DNS & Networking Issues** (Cluster internal DNS failures or unresolvable domain names)
- 🚀 **Deployment Rollout Failures** (Stuck rollouts, degraded replica sets)

---

# 📋 Operating & Setup Instructions

## 🐳 1. Run Locally with Docker Compose (Easiest Way!)

Run the entire platform with a single command:

```bash
# 1. Clone the repository
git clone https://github.com/singhdeepanshu20-droid/AI-DevOps-Kubernetes-Agent.git
cd AI-DevOps-Kubernetes-Agent

# 2. Copy environment variables
cp .env.example .env
cp backend/.env.example backend/.env

# 3. Start Frontend & Backend containers
docker compose up --build
```

- 🖥️ **Frontend Dashboard**: Open `http://localhost:3000`
- ⚙️ **Backend API**: Running at `http://localhost:8000`
- ☸️ *Note: Docker automatically mounts your local `~/.kube/config` to inspect local Kubernetes clusters.*

---

## 💻 2. Run Locally with Python & Node.js (Manual Setup)

### ⚙️ Step A: Start FastAPI Backend
```bash
# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Launch FastAPI server
cd backend
../venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 🖥️ Step B: Start Next.js Frontend
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## ⚡ 3. Test Real Kubernetes Failure Scenarios

Test how the AI Agent detects live cluster failures using 4 pre-built scenario manifests:

```bash
# 💥 Test 1: CrashLoopBackOff (Missing Database URL env var)
kubectl apply -f k8s_test_scenarios/01-crashloopbackoff.yaml

# 📦 Test 2: ImagePullBackOff (Non-existent container image tag)
kubectl apply -f k8s_test_scenarios/02-imagepullbackoff.yaml

# 🧠 Test 3: OOMKilled (Pod exceeding strict memory limits)
kubectl apply -f k8s_test_scenarios/03-oomkilled.yaml

# 🔀 Test 4: Service Selector Mismatch (Service pointing to wrong pod labels)
kubectl apply -f k8s_test_scenarios/04-service-selector-mismatch.yaml
```

Now open `http://localhost:3000`, select your cluster card (e.g. `kind-kubernetes-demo-cluster`), and click **Run Investigation**!

---

## ☁️ 4. End-to-End AWS Cloud Deployment Guide

Follow these steps to deploy on production AWS infrastructure:

### 🔑 Step 1: Configure AWS CLI & IAM
```bash
aws configure
# Set AWS Region: ap-southeast-2 (or your preferred region)
```
Ensure your IAM user/role has permissions for `AmazonBedrockFullAccess`, `AmazonDynamoDBFullAccess`, and `AmazonEKSClusterPolicy`.

### 🤖 Step 2: Enable AWS Bedrock Model Access
1. Open **AWS Console** $\rightarrow$ **AWS Bedrock** $\rightarrow$ **Model Access**.
2. Request access for **Qwen / Bedrock Models** (`qwen.qwen3-coder-next`).

### ⚡ Step 3: Initialize AWS DynamoDB Audit Table
```bash
python backend/scripts/init_dynamodb.py
```

### ☸️ Step 4: Connect to AWS EKS Cluster
```bash
aws eks update-kubeconfig --region ap-southeast-2 --name your-eks-cluster
```

### 🔐 Step 5: AWS Cognito Auth Setup
1. Create a User Pool in **AWS Cognito** (`k8s-agent-user-pool`).
2. Update `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_ENABLE_COGNITO=true
   NEXT_PUBLIC_COGNITO_USER_POOL_ID=ap-southeast-2_xxxxxxxxx
   NEXT_PUBLIC_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 🚀 Step 6: Deploy Backend Container to AWS ECR & App Runner / ECS
```bash
aws ecr create-repository --repository-name k8s-agent-backend --region ap-southeast-2
docker build -t <aws_account_id>.dkr.ecr.ap-southeast-2.amazonaws.com/k8s-agent-backend:latest ./backend
docker push <aws_account_id>.dkr.ecr.ap-southeast-2.amazonaws.com/k8s-agent-backend:latest
```

---

## 🧹 5. Complete Cleanup Guide

### 🐳 1. Docker Compose Teardown
```bash
docker compose down -v
```

### 💻 2. Stop Local Terminal Processes
```bash
lsof -ti :8000 | xargs kill -9   # Stop FastAPI Backend
lsof -ti :3000 | xargs kill -9   # Stop Next.js Frontend
```

### ☸️ 3. Clean Kubernetes Test Pods
```bash
kubectl delete -f k8s_test_scenarios/01-crashloopbackoff.yaml
kubectl delete -f k8s_test_scenarios/02-imagepullbackoff.yaml
kubectl delete -f k8s_test_scenarios/03-oomkilled.yaml
kubectl delete -f k8s_test_scenarios/04-service-selector-mismatch.yaml
```

### ☁️ 4. AWS Infrastructure Cleanup
```bash
aws dynamodb delete-table --table-name K8sAgentInvestigations --region ap-southeast-2
aws ecr delete-repository --repository-name k8s-agent-backend --region ap-southeast-2 --force
```
