import json

def search_runbook(keywords: str, filepath: str = "../data/runbooks.json") -> dict:
    """Search runbooks by keywords — returns best matching runbook."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        keywords_lower = keywords.lower().split()
        best_match = None
        best_score = 0

        for rb in data["runbooks"]:
            score = 0
            for trigger in rb["triggers"]:
                for kw in keywords_lower:
                    if kw in trigger.lower():
                        score += 1
            if score > best_score:
                best_score = score
                best_match = rb

        if best_match:
            return {
                "found":    True,
                "score":    best_score,
                "runbook":  best_match
            }
        return {
            "found":   False,
            "message": "No matching runbook found"
        }

    except Exception as e:
        raise Exception(f"Runbook search failed: {str(e)}")


if __name__ == "__main__":
    result = search_runbook("connection pool exhausted database")
    if result["found"]:
        rb = result["runbook"]
        print(f"Found: {rb['title']} [{rb['severity']}]")
        print("Steps:")
        for step in rb["steps"]:
            print(f"  {step}")