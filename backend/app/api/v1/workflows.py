from fastapi import APIRouter

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.get("/")
async def list_workflows():
    return {"workflows": []}
