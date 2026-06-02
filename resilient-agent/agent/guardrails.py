import re
import logging

logger = logging.getLogger(__name__)

# Blocked keywords
BLOCKED_INPUT = ["ignore previous", "jailbreak", "dan mode", "bypass", "forget instructions"]
BLOCKED_OUTPUT = ["as an ai, i cannot", "i am not able to provide"]

PII_PATTERNS = {
    "email":   r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone":   r'\b\d{10}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',
    "api_key": r'(sk-|tfy-)[A-Za-z0-9]{20,}',
}

def check_input(text: str) -> dict:
    text_lower = text.lower()
    
    for keyword in BLOCKED_INPUT:
        if keyword in text_lower:
            logger.warning(f"Blocked input — keyword: {keyword}")
            return {"safe": False, "reason": f"Blocked keyword: '{keyword}'"}
    
    if len(text.strip()) < 5:
        return {"safe": False, "reason": "Input too short"}
    
    if len(text) > 5000:
        return {"safe": False, "reason": "Input too long (max 5000 chars)"}

    logger.info("Input check passed")
    return {"safe": True}

def redact_pii(text: str) -> str:
    for label, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            logger.warning(f"PII detected and redacted: {label}")
        text = re.sub(pattern, f"[REDACTED-{label.upper()}]", text)
    return text

def check_output(text: str) -> dict:
    text_lower = text.lower()
    
    for phrase in BLOCKED_OUTPUT:
        if phrase in text_lower:
            logger.warning(f"Suspicious output detected: {phrase}")
            return {"safe": False, "reason": f"Model refused or gave unsafe output"}
    
    if len(text.strip()) < 10:
        return {"safe": False, "reason": "Output too short — possible failure"}

    logger.info("Output check passed")
    return {"safe": True}

def validate_tool_args(tool_name: str, kwargs: dict) -> dict:
    if tool_name == "web_search":
        q = kwargs.get("query", "")
        if not q or len(q) < 3:
            return {"safe": False, "reason": "Search query too short"}
        if any(b in q.lower() for b in BLOCKED_INPUT):
            return {"safe": False, "reason": "Blocked content in search query"}
    
    if tool_name == "read_file":
        path = kwargs.get("filepath", "")
        if ".." in path or path.startswith("/etc") or path.startswith("C:\\Windows"):
            return {"safe": False, "reason": "Dangerous file path blocked"}
    
    if tool_name == "calculate":
        expr = kwargs.get("expression", "")
        if "__" in expr or "import" in expr:
            return {"safe": False, "reason": "Dangerous expression blocked"}

    return {"safe": True}

if __name__ == "__main__":
    # Test cases
    print(check_input("What is renewable energy?"))
    print(check_input("jailbreak mode on"))
    print(redact_pii("Contact me at test@email.com or 9876543210"))
    print(validate_tool_args("read_file", {"filepath": "../../etc/passwd"}))
    print(validate_tool_args("web_search", {"query": "solar energy"}))