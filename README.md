# 🚀 AI DevOps Kubernetes Agent (AWS Bedrock + SRE AI Engine)

Welcome to the **AI DevOps Kubernetes Agent**! 

Whether you are a **non-technical manager**, a **student beginner**, or a **senior SRE engineer**, this guide explains everything in simple, plain English with zero jargon confusion.

---

## 🏛️ High-Level System Architecture

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

### 🏛️ Architecture Layer Breakdown

| Layer | Component | Core Responsibility | Key Technology |
| :--- | :--- | :--- | :--- |
| **1. Kubernetes Cluster** | **Target Infrastructure** | Running application workloads, generating logs, events, and container exit codes. | Kind, Minikube, AWS EKS |
| **2. Collector / Inspector** | **Kubectl Collector** | Non-blocking execution of `kubectl` commands with 8s timeouts to collect pod, log, event, and network states. | Python Subprocess, Kubectl CLI |
| **3. AI Reasoning Brain** | **AWS Bedrock Runtime** | SRE AI model (`qwen.qwen3-coder-next`) that synthesizes raw evidence into root causes and copyable fixes. | AWS Bedrock, Boto3 Converse API |
| **4. Core API Engine** | **FastAPI Backend Server** | User authentication, investigation orchestration, streaming real-time SSE updates, and DB persistence. | FastAPI, Python 3.9+, Asyncio |
| **5. Identity & Security** | **AWS Cognito** | Manages SRE Engineer authentication, JWT token verification, and local mock testing mode. | AWS Cognito User Pool, JWT Tokens |
| **6. Audit Storage** | **AWS DynamoDB** | Stores historical investigation reports with timestamps, confidence scores, and fix commands. | AWS DynamoDB Table |
| **7. Dashboard UI** | **Next.js 14 Frontend** | Interactive cluster cards, streaming progress bar, root cause warning banners, and past incident logs. | Next.js 14, React, Tailwind CSS |

---

## 🔄 End-to-End Workflow

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

## 🚨 Example Failure Flow

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

## 💡 What is this project? (The 1-Minute Story)

Imagine a huge factory with **hundreds of robots** (containers in Kubernetes). Every now and then, a robot stops working:
- Maybe it ran out of fuel (Memory / OOMKilled).
- Maybe someone gave it the wrong instruction manual (CrashLoopBackOff).
- Maybe it couldn't find the delivery truck (ImagePullBackOff).

Usually, human engineers have to read thousands of lines of scary log files to figure out why the robot stopped. 

**Our AI DevOps Agent is like a Super SRE Doctor.** It scans the entire factory, finds the broken robot in seconds, tells you **EXACTLY** why it broke, and gives you a single command to fix it!

---

## 🎨 1. Why do we have Frontend and Backend?

Think of our app like a car:

### 🖥️ Frontend (The Dashboard & Steering Wheel - Next.js 14)
- **What it is:** The beautiful web screen you see in your browser (`http://localhost:3000`).
- **Why we built it:** Nobody likes ugly text screens. The frontend gives you:
  - **Cluster Cards:** Clickable tiles to pick your target Kubernetes cluster (Kind, Minikube, or EKS).
  - **Live Progress Bar:** Shows real-time progress while scanning your cluster (`Checking Pods` ➔ `Reading Logs` ➔ `AI Reasoning`).
  - **Root Cause Warning Card:** Red/Amber warning banner showing the exact problem, AI confidence score, explanation, and a copyable `kubectl` fix command.

### ⚙️ Backend (The Engine & Brain - FastAPI + Python)
- **What it is:** The fast server running quietly in the background (`http://localhost:8000`).
- **Why we built it:** 
  - **Inspector:** Connects to Kubernetes and collects logs, events, pod statuses, and deployments in under 8 seconds.
  - **AI Engine:** Sends the collected logs to **AWS Bedrock Qwen AI** to figure out the root cause.
  - **Database Recorder:** Saves every past investigation into **AWS DynamoDB** so you never lose history.

---

## 🏗️ 2. How Everything Connects (Data Flow & Signals)

The investigation pipeline connects the user, backend services, AI models, and database in 4 main steps:

1. **Trigger & Authorization**: User clicks **Run Investigation** on the Next.js Frontend Dashboard. The request is authorized via JWT Bearer Token (AWS Cognito / local mock) and sent to the FastAPI backend (`POST /api/v1/investigate`).
2. **Kubernetes Signal Gathering**: The FastAPI backend executes non-blocking `kubectl` subprocess calls with an 8-second timeout across 5 inspection dimensions (Pods, Container Logs, Warning Events, Deployment Rollouts, Network Services).
3. **AI Reasoning Engine**: The collected diagnostic evidence payload is formatted into an SRE prompt and sent to **AWS Bedrock Runtime** (`qwen.qwen3-coder-next`). The AI correlates all signals and generates a structured root cause diagnosis, confidence score, and copyable `kubectl` fix command.
4. **Realtime SSE Streaming & Persistence**: The diagnosis is saved into **AWS DynamoDB** (`K8sAgentInvestigations`) for audit history, while real-time progress steps and the final diagnosis banner are streamed live back to the Frontend UI via Server-Sent Events (SSE).

---

## ☁️ 3. AWS Services & Cognito Auth (Simple Breakdown)

| AWS Service | What it does in our app | Environment Config |
| :--- | :--- | :--- |
| **AWS Bedrock** | The AI brain (`qwen.qwen3-coder-next`). Reads broken pod logs and outputs beginner-friendly root cause explanations and fixes. | `AWS_BEDROCK_MODEL_ID=qwen.qwen3-coder-next` |
| **AWS DynamoDB** | The history database (`K8sAgentInvestigations`). Stores past investigation records so you can audit previous cluster issues. | `AWS_DYNAMODB_TABLE=K8sAgentInvestigations` |
| **AWS Cognito** | The security guard. Manages user logins and OAuth tokens to ensure only authorized SRE engineers can inspect clusters. | `NEXT_PUBLIC_ENABLE_COGNITO=false` (Local) / `true` (Prod) |

### 🔐 AWS Cognito: Local Mock vs Production Mode
- **Local Development Mode (`NEXT_PUBLIC_ENABLE_COGNITO=false`)**:
  - When running locally, Cognito is **mocked/bypassed** using browser `localStorage` (`aws_user_session`). This allows developers to work instantly without setting up AWS Cognito User Pools.
- **Production Mode (`NEXT_PUBLIC_ENABLE_COGNITO=true`)**:
  - Redirects users to the official AWS Cognito Hosted Login Page.
  - Sends a secure JWT Token in HTTP Headers (`Authorization: Bearer <JWT_TOKEN>`).
  - FastAPI verifies the token with AWS Cognito JWKS public keys before running cluster commands.

---

## ☁️ 4. End-to-End AWS Production Setup & Deployment Guide

Want to deploy this system completely on **AWS Production Infrastructure** just like we built it? Follow these step-by-step instructions:

### Step 1: AWS Credentials & IAM Setup
1. Create an AWS IAM User / Role with policy permissions:
   - `AmazonBedrockFullAccess`
   - `AmazonDynamoDBFullAccess`
   - `AmazonEKSClusterPolicy`
2. Configure AWS CLI on your system:
   ```bash
   aws configure
   # AWS Access Key ID: YOUR_ACCESS_KEY
   # AWS Secret Access Key: YOUR_SECRET_KEY
   # Default region name: ap-southeast-2
   ```

---

### Step 2: Request & Enable AWS Bedrock Model Access
1. Open the **AWS Console** $\rightarrow$ Navigate to **AWS Bedrock**.
2. Click **Model Access** in the left sidebar.
3. Select **Qwen / Bedrock Models** (e.g. `qwen.qwen3-coder-next`) and click **Save Changes / Request Access**.
4. Verify access by checking `AWS_BEDROCK_MODEL_ID=qwen.qwen3-coder-next` in `backend/.env`.

---

### Step 3: Create AWS DynamoDB History Table
1. Open **AWS DynamoDB Console** $\rightarrow$ **Tables** $\rightarrow$ **Create Table**.
   - **Table Name:** `K8sAgentInvestigations`
   - **Partition Key:** `id` (String)
   - **Table Class:** Standard
2. Or initialize automatically using Python script:
   ```bash
   python backend/scripts/init_dynamodb.py
   ```

---

### Step 4: Connect to AWS EKS Cluster (Elastic Kubernetes Service)
1. Update your local `kubectl` kubeconfig to point to your live AWS EKS cluster:
   ```bash
   aws eks update-kubeconfig --region ap-southeast-2 --name eks-cluster
   ```
2. Verify node connectivity:
   ```bash
   kubectl get nodes
   ```

---

### Step 5: AWS Cognito Production Authentication Setup
1. Open **AWS Cognito Console** $\rightarrow$ **Create User Pool**.
   - **User Pool Name:** `k8s-agent-user-pool`
   - **App Client Name:** `k8s-agent-web-client`
2. Enable **Cognito Hosted UI** and configure App Client OAuth settings.
3. Set environment flag in `frontend/.env.local` to enable production authentication:
   ```env
   NEXT_PUBLIC_ENABLE_COGNITO=true
   NEXT_PUBLIC_COGNITO_USER_POOL_ID=ap-southeast-2_xxxxxxxxx
   NEXT_PUBLIC_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

### Step 6: Deploy Backend Container to AWS ECR & AWS App Runner / ECS
1. Create ECR Repository and Push Backend Image:
   ```bash
   aws ecr create-repository --repository-name k8s-agent-backend --region ap-southeast-2
   docker build -t <aws_account_id>.dkr.ecr.ap-southeast-2.amazonaws.com/k8s-agent-backend:latest ./backend
   docker push <aws_account_id>.dkr.ecr.ap-southeast-2.amazonaws.com/k8s-agent-backend:latest
   ```
2. Launch service via **AWS App Runner** or **AWS ECS Fargate**, passing the required AWS environment variables.

---

### Step 7: Deploy Frontend to AWS Amplify / Vercel
1. Deploy `frontend` directory to AWS Amplify or Vercel.
2. Set `NEXT_PUBLIC_API_BASE_URL` to your production backend URL (e.g. `https://api.yourdomain.com`).

---

## 🐳 5. How to Run Locally with Docker & Docker Compose (Easiest Way!)

Want to run the entire app with **ONE single command** before deploying to AWS? Use Docker Compose!

### Prerequisites
- Install **Docker Desktop** on Mac/Windows/Linux.
- A local Kubernetes cluster (`kind` or `minikube`) or running `kubectl`.

### Step 1: Clone Repository
```bash
git clone https://github.com/singhdeepanshu20-droid/AI-DevOps-Kubernetes-Agent.git
cd AI-DevOps-Kubernetes-Agent
```

### Step 2: Set Environment Variables
Copy `.env.example` to `.env` in the root folder and in `backend/`:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

### Step 3: Run with Docker Compose
```bash
docker compose up --build
```

That's it! 
- **Frontend App:** Open `http://localhost:3000` in your browser.
- **Backend API:** Live at `http://localhost:8000`.
- *Note:* Docker automatically mounts your local `~/.kube/config` so the backend container can read your Kubernetes clusters.

---

## 🛠️ 6. How to Run Locally Without Docker (Python + Node.js)

If you prefer running Frontend and Backend manually in separate terminals:

### Step 1: Start Backend (FastAPI)
```bash
# Setup Python Environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Start Backend Server
cd backend
../venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Start Frontend (Next.js)
In a second terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## ⚡ 7. How to Test Real Kubernetes Failure Scenarios

Want to test how the AI Agent detects real cluster failures? We have 4 pre-built test manifests!

Run any of these `kubectl` commands in your terminal:

```bash
# Test 1: Pod crashing due to missing database URL (CrashLoopBackOff)
kubectl apply -f k8s_test_scenarios/01-crashloopbackoff.yaml

# Test 2: Pod failing due to non-existent image tag (ImagePullBackOff)
kubectl apply -f k8s_test_scenarios/02-imagepullbackoff.yaml

# Test 3: Pod exceeding memory limits (OOMKilled)
kubectl apply -f k8s_test_scenarios/03-oomkilled.yaml

# Test 4: Service pointing to non-existent pod labels
kubectl apply -f k8s_test_scenarios/04-service-selector-mismatch.yaml
```

Now open `http://localhost:3000`, select your cluster card (e.g., `kind-kubernetes-demo-cluster`), click **Run Investigation**, and watch the AI Agent synthesize all issues in real-time!

---

## 🧹 8. Complete Project Cleanup Guide (Local & AWS)

When you are finished testing or want to tear down resources, follow these cleanup steps for local and AWS environments:

### 1. 🐳 Local Docker & Docker Compose Cleanup
If running via Docker Compose:
```bash
# Stop all containers, networks, and remove volumes
docker compose down -v

# (Optional) Clean up unused Docker images
docker system prune -f
```

---

### 2. 💻 Local Development Process Cleanup (Python + Node.js)
If running servers directly in your terminal:
```bash
# Stop FastAPI Backend (Kill process on port 8000)
lsof -ti :8000 | xargs kill -9

# Stop Next.js Frontend (Kill process on port 3000)
lsof -ti :3000 | xargs kill -9
```

---

### 3. ☸️ Local Kubernetes Test Pods Cleanup
Remove test failure manifests from your local cluster (`Kind` / `Minikube`):
```bash
kubectl delete -f k8s_test_scenarios/01-crashloopbackoff.yaml
kubectl delete -f k8s_test_scenarios/02-imagepullbackoff.yaml
kubectl delete -f k8s_test_scenarios/03-oomkilled.yaml
kubectl delete -f k8s_test_scenarios/04-service-selector-mismatch.yaml

# Delete any manual test pods
kubectl delete pod nginx-crash nginx-imagepullbackoff --ignore-not-found
```

---

### 4. ☁️ AWS Cloud Infrastructure Teardown

If you deployed resources to AWS, run these commands to avoid unnecessary AWS costs:

#### A. Delete AWS DynamoDB Table
```bash
aws dynamodb delete-table --table-name K8sAgentInvestigations --region ap-southeast-2
```

#### B. Delete AWS ECR Backend Repository & Images
```bash
aws ecr delete-repository --repository-name k8s-agent-backend --region ap-southeast-2 --force
```

#### C. Delete AWS Cognito User Pool
```bash
# List User Pools to find YOUR_USER_POOL_ID
aws cognito-idp list-user-pools --max-results 10 --region ap-southeast-2

# Delete Cognito User Pool
aws cognito-idp delete-user-pool --user-pool-id YOUR_USER_POOL_ID --region ap-southeast-2
```

#### D. Delete AWS EKS Cluster (If created for testing)
```bash
aws eks delete-cluster --name eks-cluster --region ap-southeast-2
```
