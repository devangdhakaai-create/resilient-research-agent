import random
from datetime import datetime

def get_metrics(service: str = "payment-service") -> dict:
    """Mock real-time metrics for a service."""
    try:
        # Simulated metrics — in real world this hits Prometheus/Datadog
        metrics = {
            "service":          service,
            "timestamp":        datetime.now().isoformat(),
            "cpu_percent":      round(random.uniform(60, 95), 1),
            "memory_percent":   round(random.uniform(70, 90), 1),
            "error_rate":       round(random.uniform(5, 40), 1),
            "avg_latency_ms":   random.randint(800, 3000),
            "active_db_conn":   random.randint(15, 20),
            "max_db_conn":      20,
            "requests_per_min": random.randint(50, 200),
            "health":           "DEGRADED"
        }

        # Auto flags
        metrics["flags"] = []
        if metrics["cpu_percent"] > 85:
            metrics["flags"].append("HIGH_CPU")
        if metrics["active_db_conn"] >= metrics["max_db_conn"]:
            metrics["flags"].append("DB_POOL_EXHAUSTED")
        if metrics["avg_latency_ms"] > 1000:
            metrics["flags"].append("HIGH_LATENCY")
        if metrics["error_rate"] > 10:
            metrics["flags"].append("HIGH_ERROR_RATE")

        return metrics

    except Exception as e:
        raise Exception(f"Metrics fetch failed: {str(e)}")


if __name__ == "__main__":
    m = get_metrics()
    print(f"Service: {m['service']}")
    print(f"CPU: {m['cpu_percent']}%")
    print(f"DB Connections: {m['active_db_conn']}/{m['max_db_conn']}")
    print(f"Flags: {m['flags']}")