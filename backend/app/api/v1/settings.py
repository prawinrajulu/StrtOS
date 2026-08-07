from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/")
async def get_settings():
    return {"tier": "ENTERPRISE", "version": "0.9"}
