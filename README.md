# 🚀 AI DevOps Kubernetes Agent (AWS Bedrock + SRE AI Engine)

> **Simple 10-Year-Old Explanation:** Imagine Kubernetes is like a giant school with hundreds of robotic classrooms (containers). When a robot breaks down or forgets its instructions, normal teachers get confused reading thousands of error log lines. Our **AI DevOps Agent** acts like a Super SRE Teacher—it automatically inspects the broken classroom, finds out why the robot crashed (e.g. missing fuel, wrong picture tag, or running out of memory), and writes down the exact step-by-step fix command!

---

## 🎨 1. What We Built & Why (Frontend + Backend Roles)

### 🖥️ Why Frontend (Next.js 14 + Tailwind CSS + Glassmorphism UI)?
- **Purpose**: Gives DevOps engineers a clean dashboard to select Kubernetes clusters (Tile Format: Kind, Minikube, EKS), trigger real-time SSE investigations, and view root causes with visual warning banners.
- **Key Features**:
  - **Cluster Selector Cards**: Interactive tile cards to select target cluster contexts.
  - **Real-Time Progress Card**: Streaming status bar for steps (`Checking Pods`, `Reading Logs`, `Analyzing Events`, `AI Reasoning`).
  - **AI Diagnosis Root Cause Card**: Shows confidence score, exact root cause, explanation, step-by-step fix, and copyable `kubectl` command.

### ⚙️ Why Backend (FastAPI + Python + Boto3 + Async SSE)?
- **Purpose**: Acts as the brain and engine of the system.
- **Key Features**:
  - **Kubernetes Evidence Collector**: Non-blocking `kubectl` execution with strict 8s timeouts to gather Pod states, logs, events, deployments, and services.
  - **AI Reasoning Engine**: Integrates AWS Bedrock Qwen (`qwen.qwen3-coder-next`) / OpenRouter to generate SRE root cause analysis.
  - **AWS DynamoDB History Service**: Persists investigation records for auditability and historical tracking.
  - **SSE Progress Streaming**: Streams live investigation steps to the frontend without freezing the UI.

---

## 🏗️ 2. Architecture & Interactive Flow Diagram

```mermaid
flowchart TD
    User([👨‍💻 DevOps / SRE User]) -->|1. Select Cluster & Click Investigate| UI[🖥️ Next.js 14 Frontend]
    UI -->|2. GET /investigate/stream| FastAPI[⚙️ FastAPI Backend Server]
    
    subgraph Evidence_Collector [🔎 Kubernetes Evidence Collector]
        FastAPI -->|3. Non-blocking Async kubectl| K8s[☸️ Kubernetes Cluster (Kind / Minikube / EKS)]
        K8s -->|Gather Pods, Logs, Events, Services| Evidence[📋 Diagnostic Evidence Payload]
    end

    subgraph AI_Reasoning_Engine [🤖 AWS AI Engine]
        Evidence -->|4. Analyze Evidence Payload| Bedrock[☁️ AWS Bedrock Qwen3 Coder Next]
        Bedrock -->|Return JSON Root Cause & Fix| AI_Result[💡 SRE Diagnosis]
    end

    subgraph Storage_Audit [💾 Persistence & History]
        AI_Result -->|5. Save Investigation Record| DynamoDB[(⚡ AWS DynamoDB)]
    end

    AI_Result -->|6. Stream SSE Progress & Final Result| UI
    UI -->|7. Render Root Cause Card & Copyable Fix| User
```

---

## 🛠️ 3. AWS Services & Integration (Detailed Guide)

| AWS Service | Role & Integration Details | Environment Config |
| :--- | :--- | :--- |
| **AWS Bedrock** | Primary SRE AI Model (`qwen.qwen3-coder-next`). Analyzes structured Kubernetes evidence payload and generates root cause, fix steps, and exact `kubectl` command. | `AWS_BEDROCK_MODEL_ID=qwen.qwen3-coder-next`, `AWS_REGION=ap-southeast-2` |
| **AWS DynamoDB** | Storage database table (`K8sAgentInvestigations`). Automatically saves past investigation history with timestamps, confidence scores, and fixes. | `AWS_DYNAMODB_TABLE=K8sAgentInvestigations` |
| **AWS Cognito** | Multi-tenant Auth & Security User Pool. Manages SRE Engineer login sessions, OAuth tokens, and RBAC backend JWT validation. | `NEXT_PUBLIC_ENABLE_COGNITO=false` (Local Mock) / `true` (Production) |

### 🔑 How AWS Cognito Authentication Works (Local Mock vs Production):
1. **Local Mock Mode (`NEXT_PUBLIC_ENABLE_COGNITO=false`)**:
   - Allows developers to run and test locally without creating AWS Cognito User Pools.
   - Bypasses Cognito login with simulated local storage sessions (`aws_user_session`).
2. **Production Mode (`NEXT_PUBLIC_ENABLE_COGNITO=true`)**:
   - Redirects user to AWS Cognito Hosted UI (`https://<domain>.auth.<region>.amazoncognito.com/login`).
   - Obtains JWT ID Token (`Bearer Token`).
   - Frontend sends `Authorization: Bearer <TOKEN>` in HTTP headers.
   - FastAPI Backend verifies token using Cognito JWKS public key before executing `kubectl` commands.

---

## ⚡ 4. Real Failure Scenarios Supported & Tested

Our agent automatically detects and synthesizes single AND multiple failures across 4 real Kubernetes test manifests:

1. **`01-crashloopbackoff.yaml`**: Pod crashes due to missing environment variable (`REQUIRED_DB_URL`).
2. **`02-imagepullbackoff.yaml`**: Pod fails to start because image tag does not exist (`nginx:this-tag-does-not-exist`).
3. **`03-oomkilled.yaml`**: Pod memory exceeds configured limit (Allocates 50MB with 10MB limit).
4. **`04-service-selector-mismatch.yaml`**: Service selector does not match pod labels.

*Multi-pod synthesis:* If 3 pods are failing at once, the agent aggregates all 3 into:
`Multiple Unhealthy Pods: nginx-crash (Error), nginx-imagepullbackoff (ImagePullBackOff), test-oomkilled (CrashLoopBackOff)`.

---

## 🚀 5. How to Run the Project (Step-by-Step Guide)

### Prerequisites
- Python 3.9+
- Node.js 18+
- `kubectl` installed
- Local Kubernetes cluster (`kind` or `minikube`) or AWS EKS

---

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/singhdeepanshu20-droid/AI-DevOps-Kubernetes-Agent.git
cd AI-DevOps-Kubernetes-Agent

# Setup Python Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

---

### Step 2: Configure Environment Variables
Copy `.env.example` in root and `backend/`:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your AWS Credentials or fallback keys:
```env
AWS_REGION=ap-southeast-2
AWS_ACCESS_KEY_ID=your-key-id
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_BEDROCK_MODEL_ID=qwen.qwen3-coder-next
AWS_DYNAMODB_TABLE=K8sAgentInvestigations
```

Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_COGNITO=false
```

---

### Step 3: Start FastAPI Backend Server
```bash
cd backend
../venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend health check:* Visit `http://localhost:8000/health` or `http://localhost:8000/clusters`.

---

### Step 4: Start Next.js Frontend Server
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*Frontend UI:* Open your browser at `http://localhost:3000`.

---

### Step 5: Test Real Failure Scenarios
Deploy test failing pods to your cluster:
```bash
# 1. CrashLoopBackOff test
kubectl apply -f k8s_test_scenarios/01-crashloopbackoff.yaml

# 2. ImagePullBackOff test
kubectl apply -f k8s_test_scenarios/02-imagepullbackoff.yaml

# 3. OOMKilled test
kubectl apply -f k8s_test_scenarios/03-oomkilled.yaml
```

Now open `http://localhost:3000`, select your cluster card (e.g. `kind-kubernetes-demo-cluster`), click **Run Investigation**, and watch the SRE AI Agent diagnose all issues in real-time!
