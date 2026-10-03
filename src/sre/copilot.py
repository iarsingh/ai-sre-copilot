TOOLS = ["list_alerts", "read_logs", "check_manifest"]

def investigate(snapshot):
    if str(snapshot.get("image", "")).endswith(":latest"):
        return {"refused": True, "reason": "latest is refused.", "hypothesis": None, "tools": TOOLS, "confirmed_root_cause": False, "paged": False}
    hypothesis = None
    if snapshot.get("reason") == "OOMKilled" and snapshot.get("memory_percent", 0) >= 90:
        hypothesis = "memory-limit"
    elif snapshot.get("drifted"):
        hypothesis = "gitops-drift"
    return {"refused": False, "hypothesis": hypothesis, "tools": TOOLS, "confirmed_root_cause": False, "paged": False}
