# 📜 README Generation Prompt & Template

Use this reusable prompt with any AI model (Gemini, Claude, GPT, DeepSeek, etc.) to automatically generate a clean, beginner-friendly, and professional `README.md` for any software project. It enforces the exact layout, ASCII box architecture, workflow diagrams, and emoji-rich operating instructions used in this repository.

---

### ✂️ Copy-Paste LLM Prompt Template:

```markdown
You are an expert technical documentation architect and SRE/DevOps engineer. Your task is to write a clean, simple, highly readable `README.md` for a software project based on the rules and structure below.

---

## 📐 README.md Design & Layout Rules

1. **Simplicity & Clarity First**: Avoid bloated paragraphs or overlapping flowcharts. Use clean section breaks (`---`).
2. **Visual Box Diagrams**: Represent system architecture using structured ASCII box diagrams with explicit `Responsibility:` and `Components:` for every layer.
3. **Sequential Workflow Diagrams**: Represent execution flow using clear vertical ASCII arrow trees.
4. **Emoji-Decorated Instructions**: Decorate section headers, step numbers, quickstart instructions, and cleanup steps with clean, intuitive emojis (🐳, 💻, ⚡, ☁️, 🧹, 🎯, 🏛️, 🔄, 🚨, 🛠️).
5. **Target Audience**: Plain, professional English accessible to non-technical stakeholders, students, and senior engineers alike.

---

## 📝 Mandatory README.md Layout Sequence

Your output `README.md` MUST follow this exact 7-part section sequence:

### 1. Title & Header
- `# 🚀 <Project Name> (<Key Technology Stack>)`
- A welcoming 1-2 sentence overview explaining what the app does in simple terms.

### 2. 🎯 Goal Section
- `## 🎯 Goal`
- A bulleted list of 5-8 primary capabilities, each prefixed with a relevant emoji (🔎, 📋, 🤖, 💡, ⚡, 💾, ☁️).

### 3. 🏛️ High Level Architecture Section
- `# 🏛️ High Level Architecture`
- An ASCII box diagram representing all layers from target data source/infrastructure down to frontend UI and deployment targets.
- Include explicit `Responsibility:` and `Components:` inside each box.
- Followed by an **Architecture Layer Breakdown Table** (`| Layer | Component | Core Responsibility | Key Technology |`).

### 4. 🔄 End-to-End Workflow Section
- `# 🔄 End-to-End Workflow`
- A step-by-step vertical ASCII arrow tree tracking a single request from user action to final UI display/response.

### 5. 🚨 Example Failure / Execution Flow Section
- `# 🚨 Example Failure Flow` (or `# 🚨 Example Execution Flow`)
- A concrete scenario walkthrough with key fields:
  - `Issue:`
  - `Agent Investigation:` (with `✓` checkmarks)
  - `Detected Problem:`
  - `Root Cause:`
  - `Confidence:`
  - `Suggested Fix:`
  - `Prevention:`

### 6. 🛠️ Supported Features / Problem Modes Section
- `## 🛠️ Supported <Capabilities / Problem Modes>`
- Bullet list with emoji markers (🔴, 📦, 💥, ⏳, 🛑, 🔀, 🌐, 🚀) detailing supported scenarios, errors, or feature modes.

### 7. 📋 Operating & Setup Instructions (Emoji-Rich)
- `# 📋 Operating & Setup Instructions`
- `## 🐳 1. Run Locally with Docker Compose (Easiest Way!)`
- `## 💻 2. Run Locally (Manual Setup / CLI)`
- `## ⚡ 3. Test Scenarios / Usage Commands`
- `## ☁️ 4. Cloud Production Deployment Guide`
- `## 🧹 5. Complete Cleanup Guide` (Local process kill commands, container teardown, cloud cleanup)

---

## 🤖 PROJECT CONTEXT (FILL THIS IN FOR YOUR APP)

Please write the `README.md` for the following application:

- **Project Name**: [e.g. AI DevOps Kubernetes Agent]
- **Tech Stack**: [e.g. Next.js 14, FastAPI, AWS Bedrock, AWS DynamoDB, Docker, Kubectl]
- **Target Audience / Purpose**: [e.g. Automated Kubernetes incident investigation and root-cause analysis]
- **Key Components**:
  - Target Infrastructure / Data Source: [e.g. Kind, Minikube, EKS]
  - Inspector / Collector: [e.g. Kubectl CLI subprocess collector]
  - AI Engine: [e.g. AWS Bedrock Runtime Qwen3 Coder Next]
  - Core API / Backend: [e.g. FastAPI server with SSE streaming]
  - Storage / DB: [e.g. AWS DynamoDB table]
  - Frontend UI: [e.g. Next.js 14 Dashboard]
- **Setup & Run Commands**: [Insert Docker, Local, and Test commands]
```
