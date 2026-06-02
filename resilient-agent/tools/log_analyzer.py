import re
from agent.guardrails import redact_pii

def analyze_logs(filepath: str = "../data/sample_logs.txt") -> dict:
    """Read and analyze logs — extract errors, warnings, timeline."""
    try:
        with open(filepath, "r") as f:
            raw = f.read()

        # Redact PII before processing
        safe_logs = redact_pii(raw)

        lines = safe_logs.strip().split("\n")
        
        errors, warnings, critical = [], [], []
        
        for line in lines:
            if "CRIT" in line:
                critical.append(line.strip())
            elif "ERROR" in line:
                errors.append(line.strip())
            elif "WARN" in line:
                warnings.append(line.strip())

        # Extract first error time for timeline
        first_error = errors[0] if errors else "None"
        first_crit  = critical[0] if critical else "None"

        return {
            "total_lines":    len(lines),
            "error_count":    len(errors),
            "warning_count":  len(warnings),
            "critical_count": len(critical),
            "errors":         errors,
            "warnings":       warnings,
            "critical":       critical,
            "first_error":    first_error,
            "first_critical": first_crit,
            "raw_safe":       safe_logs
        }

    except Exception as e:
        raise Exception(f"Log analysis failed: {str(e)}")


if __name__ == "__main__":
    result = analyze_logs()
    print(f"Errors: {result['error_count']}")
    print(f"Critical: {result['critical_count']}")
    print(f"First error: {result['first_error']}")