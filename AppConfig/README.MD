# AgentCore + AppConfig Powered LLM Agent

This project demonstrates an AWS Bedrock AgentCore-based LLM agent that dynamically loads configuration (such as model selection) from AWS AppConfig at runtime.

It is designed for production-style deployments where:
- LLM models can be switched without redeploying code
- Configuration is centrally managed via AWS AppConfig
- Runtime executes securely inside AgentCore using IAM roles

---

## 🚀 Architecture Overview
AgentCore Runtime
↓
IAM Execution Role
↓
AWS AppConfig (dynamic configuration)
↓
Amazon Bedrock LLM


### Key Idea
- Code is static
- Configuration is dynamic (AppConfig)
- IAM controls access securely
- AgentCore executes workloads in a managed runtime

---

## 📦 What This Project Does

- Fetches runtime configuration from AWS AppConfig
- Loads LLM model configuration dynamically (`llm.model_id`)
- Uses cached configuration for performance optimization
- Falls back safely if AppConfig fetch fails
- Runs inside AWS Bedrock AgentCore runtime

---

## ⚙️ Required AWS Setup

### 1. AWS AppConfig Setup

You must create:

- AppConfig Application
- Environment (e.g., dev / prod)
- Configuration Profile containing JSON like:

```json
{
  "llm": {
    "model_id": "apac.amazon.nova-lite-v1:0"
  }
}

### 2. IAM Permissions (Critical)

The AgentCore execution role must include permissions for:

AWS AppConfig (session + config fetch)
Amazon Bedrock model invocation
CloudWatch Logs
Minimum IAM Policy Example

```json
{
  "Effect": "Allow",
  "Action": [
    "appconfig:StartConfigurationSession",
    "appconfig:GetLatestConfiguration",
    "bedrock:InvokeModel",
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "*"
}

### Note:
For production, replace "Resource": "*" with scoped ARNs for tighter security.

### 3. Deployment Flow
agentcore configure
agentcore launch
## 🧠 Configuration Caching & Versioning

### ⏱️ TTL-Based Caching (Current Implementation)

The agent caches AppConfig responses for performance optimization.

- Cache TTL: `60 seconds`
- After TTL expiry, configuration is refreshed from AppConfig
- Reduces API calls and improves runtime latency

Flow:
1. Fetch config from AppConfig
2. Store in in-memory cache
3. Serve cached config within TTL window
4. Refresh after TTL expiry

---

### 🔁 Configuration Version Tracking

AppConfig supports versioned configurations (e.g., Version 2 → Version 4).

This system tracks configuration changes such as:
- LLM model swaps
- Parameter tuning (temperature, max_tokens)
- Prompt or behavior adjustments

#### Example Change
- Version 2: `nova-lite-v1:0`
- Version 4: `nova-micro-v1:0`

---

### 🧩 Recommended Enhancement (Optional but Strongly Suggested)

To make this production-grade, track version metadata:

```json
{
  "llm": {
    "model_id": "apac.amazon.nova-micro-v1:0"
  },
  "config_version": "4"
}