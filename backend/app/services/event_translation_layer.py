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

def translate_backend_task_to_user_task(task: Any) -> Optional[Dict[str, Any]]:
    if not task or not getattr(task, "id", None):
        return None

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

    task_title = getattr(task, "title", "Business Task")
    status_msg = "StrtOS is working"
    if status == "COMPLETED":
        status_msg = "Completed successfully"
    elif status == "FAILED":
        status_msg = f"{task_title} could not be completed"
    elif status == "BLOCKED":
        status_msg = "Waiting for required analysis"

    output = getattr(task, "output", None)
    result = extract_task_result_data(output, task_title) if status == "COMPLETED" and output else None

    agent_name = getattr(task, "agent_name", None) or task_title
    completed_at = getattr(task, "completed_at", None)
    started_at = getattr(task, "started_at", None)
    created_at = getattr(task, "created_at", None)
    timestamp_str = completed_at or started_at or created_at or "Time unavailable"

    return {
        "id": getattr(task, "id", None),
        "workflowId": getattr(task, "workflow_id", None),
        "title": task_title,
        "agentName": agent_name,
        "status": status,
        "statusMessage": status_msg,
        "timestamp": timestamp_str,
        "summary": result.get("summary") if result else ("INSUFFICIENT DATA" if status == "COMPLETED" else None),
        "errorReason": getattr(task, "error_message", None),
        "result": result
    }

def translate_workflow_to_tasks(workflow: Any, tasks: List[Any] = None) -> Dict[str, Any]:
    if not workflow or not getattr(workflow, "id", None) or not isinstance(tasks, list):
        return {
            "activeTask": None,
            "completedTasks": [],
            "upcomingTasks": []
        }
    
    translated = [translate_backend_task_to_user_task(t) for t in tasks]
    translated = [t for t in translated if t is not None]
    
    active = next((t for t in translated if t["status"] == "RUNNING"), None)
    completed = [t for t in translated if t["status"] == "COMPLETED"]
    upcoming = [t for t in translated if t["status"] in ["QUEUED", "BLOCKED"]]

    return {
        "activeTask": active,
        "completedTasks": completed,
        "upcomingTasks": upcoming
    }
