import requests
import os

def web_search(query: str) -> str:
    """Simple web search using DuckDuckGo — free, no API key needed."""
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        results = []
        if data.get("AbstractText"):
            results.append(data["AbstractText"])
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(topic["Text"])

        return "\n".join(results) if results else "No results found."
    except Exception as e:
        raise Exception(f"Search tool failed: {str(e)}")

def read_file(filepath: str) -> str:
    """Read a local file and return its content."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise Exception(f"File read failed: {str(e)}")

def calculate(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        allowed = set("0123456789+-*/()., ")
        if not all(c in allowed for c in expression):
            raise ValueError("Invalid characters in expression")
        result = eval(expression)
        return str(result)
    except Exception as e:
        raise Exception(f"Calculate failed: {str(e)}")

TOOLS = {
    "web_search": web_search,
    "read_file": read_file,
    "calculate": calculate,
}

def run_tool(name: str, **kwargs) -> str:
    if name not in TOOLS:
        raise Exception(f"Unknown tool: {name}")
    return TOOLS[name](**kwargs)

if __name__ == "__main__":
    print(run_tool("web_search", query="renewable energy adoption 2024"))
    print(run_tool("calculate", expression="30 * 1.15"))