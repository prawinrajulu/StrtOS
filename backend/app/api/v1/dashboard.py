from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/metrics")
async def get_dashboard_metrics():
    return {"active_workflows": 18, "agents_online": "8/8", "avg_confidence": 92.4, "tasks_today": 2481}
