from fastapi import APIRouter, Depends, Response

from app.schemas.usuario import UsuarioCreate, LoginRequest, UsuarioRead
from app.services import auth_service
from app.models.usuario import Usuario
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


def _set_token_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )


@router.post("/register")
def register(data: UsuarioCreate, response: Response):
    token, usuario = auth_service.register_user(data)
    _set_token_cookie(response, token)
    return {"usuario": usuario}


@router.post("/login")
def login(data: LoginRequest, response: Response):
    token, usuario = auth_service.login_user(data)
    _set_token_cookie(response, token)
    return {"usuario": usuario}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return {"message": "Sesión cerrada"}


@router.get("/me", response_model=UsuarioRead)
def me(usuario: Usuario = Depends(auth_service.get_current_user)):
    return usuario
