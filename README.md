# 🚀 AI DevOps Kubernetes Agent (AWS Bedrock + SRE AI Engine)

Welcome to the **AI DevOps Kubernetes Agent**! 

Whether you are a **non-technical manager**, a **student beginner**, or a **senior SRE engineer**, this guide explains everything in simple, plain English with zero jargon confusion.

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

## 🏗️ 2. How Everything Connects (Flow Diagram)

Here is a visual map showing how data flows step-by-step:

```mermaid
flowchart TD
    User([👨‍💻 You / DevOps Engineer]) -->|1. Click 'Run Investigation'| UI[🖥️ Next.js 14 Frontend UI]
    UI -->|2. Request Live SSE Stream| FastAPI[⚙️ FastAPI Backend Server]
    
    subgraph K8s_Collector [🔎 1. Kubernetes Inspector]
        FastAPI -->|3. Run fast kubectl commands| K8s[☸️ Kubernetes Cluster (Kind / Minikube / EKS)]
        K8s -->|Gather Pod States, Error Logs, Events| Evidence[📋 Diagnostic Evidence Payload]
    end

    subgraph AI_Engine [🤖 2. AWS Bedrock AI Brain]
        Evidence -->|4. Send Evidence Payload| Bedrock[☁️ AWS Bedrock Qwen3 Coder Next]
        Bedrock -->|Return JSON Diagnosis & Fix| AI_Result[💡 SRE Root Cause & Fix]
    end

    subgraph Storage [💾 3. AWS DynamoDB History]
        AI_Result -->|5. Save Audit Record| DynamoDB[(⚡ AWS DynamoDB Table)]
    end

    AI_Result -->|6. Stream Realtime Updates| UI
    UI -->|7. Display Red Warning Banner & Fix Command| User
```

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

## 🐳 4. How to Run Locally with Docker & Docker Compose (Easiest Way!)

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

## 🛠️ 5. How to Run Locally Without Docker (Python + Node.js)

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

## ⚡ 6. How to Test Real Kubernetes Failure Scenarios

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

## 🧹 Cleanup Test Pods
When finished testing, clean up test resources:
```bash
kubectl delete -f k8s_test_scenarios/01-crashloopbackoff.yaml
kubectl delete -f k8s_test_scenarios/02-imagepullbackoff.yaml
kubectl delete -f k8s_test_scenarios/03-oomkilled.yaml
kubectl delete -f k8s_test_scenarios/04-service-selector-mismatch.yaml
```
