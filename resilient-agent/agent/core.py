import json
import os
import sys
from datetime import datetime
from agent.gateway import call_with_fallback
from agent.guardrails import check_input, check_output, redact_pii
from tools.log_analyzer import analyze_logs
from tools.metrics import get_metrics
from tools.runbook import search_runbook
import logging

logger = logging.getLogger(__name__)

STATE_FILE = "incident_state.json"

def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    logger.info(f"State saved — step: {state['current_step']}")

def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            logger.info("Resuming from saved state...")
            return json.load(f)
    return None

def fresh_state(alert: str) -> dict:
    return {
        "alert":         alert,
        "current_step":  0,
        "steps":         [],
        "results":       {},
        "status":        "running",
        "created_at":    datetime.now().isoformat()
    }

PIPELINE = [
    "collect_data",
    "root_cause_analysis",
    "find_runbook",
    "generate_response"
]

def run_step(step_name: str, state: dict) -> dict:
    alert   = state["alert"]
    results = state["results"]

    if step_name == "collect_data":
        logs    = analyze_logs()
        metrics = get_metrics()
        content = json.dumps({
            "logs":    logs,
            "metrics": metrics
        }, indent=2)
        return {"content": content, "model_used": "tools", "fallback_level": -1}

    if step_name == "root_cause_analysis":
        logs_summary = json.dumps(results.get("collect_data", {}))
        
        # Guardrails — input check
        prompt = f"""You are a senior SRE. Analyze this production incident.

Alert: {alert}

Log Analysis & Metrics:
{logs_summary}

Identify:
1. Root cause (be specific)
2. Timeline of events
3. Impact (which services affected)
4. Severity (CRITICAL/HIGH/MEDIUM)
"""
        guard = check_input(prompt)
        if not guard["safe"]:
            raise Exception(f"Input blocked by guardrails: {guard['reason']}")

        messages = [
            {"role": "system", "content": "You are a senior SRE analyst. Be concise and technical."},
            {"role": "user",   "content": prompt}
        ]
        result = call_with_fallback(messages)

        # Guardrails — output check + PII redaction
        safe_output = redact_pii(result["content"])
        out_check   = check_output(safe_output)
        if not out_check["safe"]:
            raise Exception(f"Output blocked by guardrails: {out_check['reason']}")

        result["content"] = safe_output
        return result

    if step_name == "find_runbook":
        rca      = results.get("root_cause_analysis", "")
        keywords = "connection pool exhausted database timeout"
        rb       = search_runbook(keywords)
        content  = json.dumps(rb, indent=2)
        return {"content": content, "model_used": "tools", "fallback_level": -1}

    if step_name == "generate_response":
        rca     = results.get("root_cause_analysis", "")
        runbook = results.get("find_runbook", "")

        prompt = f"""You are a senior SRE. Generate a clear incident response report.

Root Cause Analysis:
{rca}

Recommended Runbook:
{runbook}

Generate:
1. Executive Summary (2-3 lines)
2. Immediate Actions (numbered steps)
3. Prevention Recommendations (2-3 points)
4. Estimated Resolution Time
"""
        guard = check_input(prompt)
        if not guard["safe"]:
            raise Exception(f"Input blocked: {guard['reason']}")

        messages = [
            {"role": "system", "content": "You are a senior SRE. Write clear, actionable incident reports."},
            {"role": "user",   "content": prompt}
        ]
        result      = call_with_fallback(messages)
        safe_output = redact_pii(result["content"])
        result["content"] = safe_output
        return result

def run_agent(alert: str, resume: bool = False):
    # Guardrails on incoming alert
    guard = check_input(alert)
    if not guard["safe"]:
        print(f"❌ Alert blocked by guardrails: {guard['reason']}")
        return

    state = load_state() if resume else None
    if state is None:
        state = fresh_state(alert)
        logger.info(f"New incident: {alert}")

    print(f"\n🚨 INCIDENT: {alert}")
    print("=" * 60)

    for i, step in enumerate(PIPELINE):
        if i < state["current_step"]:
            logger.info(f"Skipping done step: {step}")
            continue

        print(f"\n⚙️  Step {i+1}/{len(PIPELINE)}: {step}")

        try:
            result = run_step(step, state)
            state["results"][step]  = result["content"]
            state["current_step"]   = i + 1
            state["steps"].append({
                "step":           step,
                "model_used":     result["model_used"],
                "fallback_level": result["fallback_level"]
            })
            save_state(state)
            print(f"✅ Done (model: {result['model_used']})")

        except Exception as e:
            state["status"] = "failed"
            state["error"]  = str(e)
            save_state(state)
            logger.error(f"Step {step} failed: {e}")
            print(f"❌ Step failed: {e}")
            break

    if state["current_step"] == len(PIPELINE):
        state["status"] = "complete"
        save_state(state)
        print("\n" + "=" * 60)
        print("🎉 INCIDENT RESPONSE COMPLETE")
        print("=" * 60)
        print("\n📋 FINAL REPORT:")
        print(state["results"]["generate_response"])
        print("\n📊 MODEL USAGE:")
        for s in state["steps"]:
            fb = f"(fallback level {s['fallback_level']})" if s['fallback_level'] >= 0 else "(tool)"
            print(f"  {s['step']}: {s['model_used']} {fb}")

if __name__ == "__main__":
    alert = "CRITICAL: payment-service DOWN — database connection pool exhausted, cascading failures detected"
    run_agent(alert)