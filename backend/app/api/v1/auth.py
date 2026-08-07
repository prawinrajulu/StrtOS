from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.auth_service import AuthService
from app.schemas.all_schemas import UserCreate, LoginRequest, Token, UserRead, SuccessResponse
from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=SuccessResponse[UserRead])
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    service = AuthService(db)
    user = await service.register_user(user_in)
    return SuccessResponse(data=UserRead.model_validate(user), message="User registered successfully")

@router.post("/login", response_model=Token)
async def login(login_in: LoginRequest, db: AsyncSession = Depends(get_db_session)):
    service = AuthService(db)
    return await service.authenticate_user(login_in)

@router.get("/me", response_model=SuccessResponse[UserRead])
async def get_me(current_user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db_session)):
    service = AuthService(db)
    user = await service.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return SuccessResponse(data=UserRead.model_validate(user))
