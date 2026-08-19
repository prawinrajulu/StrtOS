from typing import Dict, Any, List, Optional

def extract_task_result_data(output: Any, title: str) -> Dict[str, Any]:
    if not output or not isinstance(output, dict):
        return {
            "title": title,
            "summary": "INSUFFICIENT DATA",
            "keyFinding": "INSUFFICIENT DATA",
            "importantChange": "INSUFFICIENT DATA",
            "businessImpact": "INSUFFICIENT DATA",
            "recommendation": "No recommendation available",
            "confidence": None,
            "findings": []
        }

    findings = output.get("findings") if isinstance(output.get("findings"), list) else []

    return {
        "title": title,
        "summary": output.get("summary") or (findings[0] if len(findings) > 0 else "INSUFFICIENT DATA"),
        "keyFinding": output.get("key_finding") or (findings[0] if len(findings) > 0 else "INSUFFICIENT DATA"),
        "importantChange": output.get("important_change") or (findings[1] if len(findings) > 1 else "INSUFFICIENT DATA"),
        "businessImpact": output.get("business_impact") or output.get("summary") or "INSUFFICIENT DATA",
        "recommendation": output.get("recommendation") or (output.get("recommendations")[0] if isinstance(output.get("recommendations"), list) and len(output.get("recommendations")) > 0 else "No recommendation available"),
        "confidence": output.get("confidence") if isinstance(output.get("confidence"), (int, float)) else None,
        "findings": findings
    }

def translate_backend_task_to_user_task(task: Any) -> Dict[str, Any]:
    status_raw = str(getattr(task, "status", "QUEUED")).upper()
    status = "QUEUED"
    
    if status_raw == "RUNNING":
        status = "RUNNING"
    elif status_raw == "COMPLETED":
        status = "COMPLETED"
    elif status_raw == "FAILED":
        status = "FAILED"
    elif status_raw in ["BLOCKED", "SKIPPED"]:
        status = "BLOCKED"

    status_msg = "StrtOS is working"
    if status == "COMPLETED":
        status_msg = "Completed successfully"
    elif status == "FAILED":
        status_msg = f"{getattr(task, 'title', 'Task')} could not be completed"
    elif status == "BLOCKED":
        status_msg = "Waiting for required analysis"

    output = getattr(task, "output", None)
    result = extract_task_result_data(output, getattr(task, "title", "Task")) if status == "COMPLETED" and output else None

    return {
        "id": getattr(task, "id", "t-1"),
        "workflowId": getattr(task, "workflow_id", "wf-1"),
        "title": getattr(task, "title", "Task"),
        "agentName": getattr(task, "agent_name", "Specialist Agent"),
        "status": status,
        "statusMessage": status_msg,
        "summary": result.get("summary") if result else ("INSUFFICIENT DATA" if status == "COMPLETED" else None),
        "errorReason": getattr(task, "error_message", None),
        "result": result
    }

def translate_workflow_to_tasks(workflow: Any, tasks: List[Any] = None) -> Dict[str, Any]:
    if not tasks:
        tasks = []
    
    translated = [translate_backend_task_to_user_task(t) for t in tasks]
    
    active = next((t for t in translated if t["status"] == "RUNNING"), None)
    completed = [t for t in translated if t["status"] == "COMPLETED"]
    upcoming = [t for t in translated if t["status"] in ["QUEUED", "BLOCKED"]]

    return {
        "activeTask": active,
        "completedTasks": completed,
        "upcomingTasks": upcoming
    }
