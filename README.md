```This project demonstrates a simple AI agent built using Strands Agents and deployed on AWS AgentCore.

The agent supports:
- tool calling
- runtime invocation
- custom tools
- cloud deployment experimentation

The goal of the project was to better understand practical agent deployment and execution workflows using managed infrastructure.
```
## Stack

- Strands Agents
- AWS AgentCore
- Amazon Bedrock
- Python
- Custom Tools

## Features

- Agent invocation through AWS AgentCore
- Tool orchestration
- Custom tool integration
- Runtime execution
- Simple deployment workflow
- Extensible agent architecture

## Challenges / Learnings

Some areas I explored while building this project:

- Understanding how agent runtime execution differs from traditional application execution
- Managing tool orchestration inside an agent workflow
- Structuring agents for deployment rather than only local execution
- Learning deployment workflows using AWS AgentCore
- Designing custom tools that can be safely invoked by the agent


# Running Strands Agent Locally

## Install Dependencies

```bash
uv sync --frozen
```

Installs all project dependencies from the lock file for reproducible builds.

---

## Run the Application

```bash
uv run python main.py
```

This starts the Strands Agent locally.

If the application runs successfully, proceed to AWS deployment for a production-ready setup.

---

# AWS Bedrock Model Setup

## Select an Inference Model

### Step 1 — Open Bedrock Console

Open the AWS Bedrock Console and navigate to:

```text
Bedrock → Inference Profiles
```

---

### Step 2 — Get Model ID

Open the required inference profile and copy the model ID or inference profile ARN.

Example:

```text
amazon.nova-micro-v1:0
```

or

```text
arn:aws:bedrock:ap-south-1:123456789012:inference-profile/abc123
```

---

### Step 3 — Configure AWS Profile

Need to setup AWS CLI 

Verify AWS access and available models:

```bash
aws bedrock list-foundation-models --region ap-south-1
```

---

### Step 4 — Run the Application

```bash
uv run python main.py
```

---

# Deploying to AWS AgentCore

This section explains how to deploy the Strands Agent to AWS AgentCore.

---

# Create Deployment Entry File

Create a new deployment file:

```text
agentcore.py
```

This file acts as the AgentCore application entrypoint.

---

# Required Changes for AgentCore Compatibility

## 1. Create AgentCore App Object

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()
```

---

## 2. Add Entrypoint Decorator

Add the AgentCore entrypoint decorator to the main handler function.

```python
@app.entrypoint
async def invoke(payload):
    ...
```

This makes the application compatible with the AgentCore runtime.

---

## 3. Create Dockerfile

Create a `Dockerfile` for containerized deployment.

The container image will be:

1. Built locally
2. Pushed to Amazon ECR
3. Deployed to AgentCore

---

## 4. Create requirements.txt

Create a `requirements.txt` file containing all Python dependencies required by the application.

Example:

```txt
bedrock-agentcore-starter-toolkit==0.1.10
boto3>=1.39.7
strands-agents==1.18.0
strands-agents-tools>=0.5.1
```

---

# Install AgentCore Toolkit

Install the AgentCore toolkit locally before deployment:

```bash
pip install bedrock-agentcore-starter-toolkit==0.1.10
```

---

# AgentCore Deployment Commands

## Configure AgentCore

```bash
agentcore configure -e agentcore.py -r ap-south-1
```

Configures the deployment environment and runtime entrypoint.
Ask for Execution role ARN/Name: Auto Create
ECR Repository: Auto Create
Auto detect dependency file - requirements.txt
Use Default IAM authorization
This will create bedrock_agentcore.yaml file that will be used during agentcore launch command

---

## Launch Deployment

```bash
agentcore launch
This will use Codebuild internally to deploy the image. Hence will have IAM role with relevant access
In case you have re-launch in case of failure/conflict, use
agentcore launch --auto-update-on-conflict
```

Builds the Docker image, pushes it to ECR, and deploys the agent to AWS AgentCore.

---

## Check Deployment Status

```bash
agentcore status
```

Displays deployment status and runtime information.

---

## Invoke the Agent

```bash
agentcore invoke "{\"prompt\": \"what is the time now\"}"
```

Tests the deployed agent by sending a prompt request.

---

## Destroy Deployment

```bash
agentcore destroy
```

Removes all deployed AgentCore resources.

---

# Deployment Flow

```text
Local Strands Agent
        ↓
Create AgentCore Entrypoint
        ↓
Create Dockerfile
        ↓
Build Container Image
        ↓
Push Image to Amazon ECR
        ↓
Deploy to AWS AgentCore
        ↓
Invoke Agent Endpoint
```

# Docker Configuration Overview

This project uses Docker to package and run a Strands + AgentCore application with AWS Bedrock integration and OpenTelemetry monitoring.

---

# Base Image

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
```

Uses:

- Python 3.12
- Debian Bookworm Slim
- Preinstalled `uv` package manager for faster dependency installation

---

# Working Directory

```dockerfile
WORKDIR /app
```

Sets `/app` as the container working directory where the application code will run.

---

# UV Configuration

```dockerfile
ENV UV_SYSTEM_PYTHON=1
ENV UV_COMPILE_BYTECODE=1
```

Configuration:

- `UV_SYSTEM_PYTHON=1` → installs packages directly into system Python
- `UV_COMPILE_BYTECODE=1` → precompiles `.pyc` files for faster startup

---

# Install Dependencies

```dockerfile
COPY requirements.txt .
RUN uv pip install -r requirements.txt
```

Copies dependency file and installs all required Python packages.

---

# OpenTelemetry Support

```dockerfile
RUN uv pip install "aws-opentelemetry-distro>=0.10.1"
```

Adds AWS OpenTelemetry instrumentation for:

- tracing
- metrics
- observability
- distributed monitoring

---

# AWS Region Configuration

```dockerfile
ENV AWS_REGION=ap-south-1
ENV AWS_DEFAULT_REGION=ap-south-1
```

Configures the default AWS region for boto3 and Bedrock API calls.

---

# Docker Runtime Detection

```dockerfile
ENV DOCKER_CONTAINER=1
```

Custom environment variable used by the application to detect containerized execution.

Example:

```python
if os.getenv("DOCKER_CONTAINER"):
    host = "0.0.0.0"
```

---

# Security Best Practice

```dockerfile
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore
```

Creates and uses a non-root user for improved container security.

---

# Copy Application Code

```dockerfile
COPY . .
```

Copies the complete project into the container while respecting `.dockerignore`.

---

# Exposed Ports

```dockerfile
EXPOSE 8080
EXPOSE 8000
```

Common usage:

| Port | Purpose |
|---|---|
| 8080 | Main API/Application |
| 8000 | Development or secondary service |

---

# Application Startup

```dockerfile
CMD ["opentelemetry-instrument", "python", "-m", "agentcore"]
```

Container startup flow:

1. Starts OpenTelemetry instrumentation
2. Launches Python module `agentcore`
3. Enables tracing and monitoring automatically

Equivalent command:

```bash
opentelemetry-instrument python -m agentcore
```

---

# Build Docker Image

```bash
docker build -t strands-agent .
```

---

# Run Container

```bash
docker run -p 8080:8080 strands-agent
```

Run with AWS credentials:

```bash
docker run \
-e AWS_ACCESS_KEY_ID=xxx \
-e AWS_SECRET_ACCESS_KEY=xxx \
-e AWS_SESSION_TOKEN=xxx \
-p 8080:8080 \
strands-agent
```

---

# Recommended Python Version

Python 3.11 or 3.12 is recommended for better compatibility with:

- Strands Agents
- AWS Bedrock SDK
- boto3
- OpenTelemetry libraries
```