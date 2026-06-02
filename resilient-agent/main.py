import sys
from agent.core import run_agent

SAMPLE_ALERTS = {
    "1": "CRITICAL: payment-service DOWN — database connection pool exhausted, cascading failures detected",
    "2": "HIGH: checkout-service response time 3200ms — exceeding 800ms threshold",
    "3": "CRITICAL: order-service cannot reach payment-service — downstream cascade detected",
}

if __name__ == "__main__":
    print("\n🚨 PRODUCTION INCIDENT RESPONSE AGENT")
    print("="*60)
    print("Select alert to simulate:")
    for k, v in SAMPLE_ALERTS.items():
        print(f"  [{k}] {v[:70]}...")
    print("  [c] Custom alert")
    print("  [r] Resume last incident")

    choice = input("\nChoice: ").strip()

    if choice == "r":
        alert = input("Alert description: ").strip()
        run_agent(alert, resume=True)
    elif choice == "c":
        alert = input("Enter alert: ").strip()
        run_agent(alert)
    elif choice in SAMPLE_ALERTS:
        run_agent(SAMPLE_ALERTS[choice])
    else:
        print("Invalid choice")
        sys.exit(1)