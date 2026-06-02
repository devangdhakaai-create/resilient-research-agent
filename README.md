# 🛡️ Resilient Incident Response Agent

> Built for TrueFoundry Resilient Agents Hackathon 2026

An AI agent that automatically responds to production incidents — even when models fail, rate limits hit, or tools break.

## 🎯 What It Does
- Detects production alerts and analyzes logs + metrics
- Finds matching runbook automatically  
- Generates actionable incident response report
- **Never crashes** — fallback models + state persistence

## 🏗️ Architecture
Alert → Guardrails → Agent Core → TrueFoundry AI Gateway
↓
Primary: Gemini 2.5 Flash Lite
Fallback 1: Amazon Nova Micro
Fallback 2: Amazon Nova Lite

## 🛡️ Resilience Features
| Failure | How Agent Handles It |
|---|---|
| Rate limit hit | Auto-fallback to next model |
| Model timeout | Retry with exponential backoff |
| Tool failure | Caught + logged, agent continues |
| Mid-run crash | State saved — resumes from last step |
| Malicious input | Guardrails block before LLM call |
| PII in output | Auto-redacted before storing |

## 🚀 Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/resilient-research-agent
cd resilient-research-agent/resilient-agent
pip install -r requirements.txt
cp .env.example .env  # Add your keys
python main.py
```

## 🧪 Run Stress Tests
```bash
python stress_test.py
```

## 🔧 Stack
- **TrueFoundry AI Gateway** — routing, fallback, observability
- **AWS Bedrock** — Nova Micro + Nova Lite (fallback models)
- **Google Gemini 2.5 Flash Lite** — primary model (free tier)
- **TrueFoundry Guardrails** — input/output safety
- **Tenacity** — retry with exponential backoff
