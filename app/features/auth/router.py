from fastapi import APIRouter, Request, Depends
from app.features.auth import service
from app.features.auth.schemas import LoginRequest, LoginResponse, UserOut
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse, response_model_by_alias=True)
def login(body: LoginRequest, request: Request):
    ip = request.client.host if request.client else "unknown"
    return service.login(body.usuario, body.clave, ip)

@router.get("/me", response_model=UserOut, response_model_by_alias=True)
def me(payload: dict = Depends(get_current_user)):
    return service.get_me(int(payload["sub"]))