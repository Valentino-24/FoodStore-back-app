from fastapi import APIRouter, Depends, Response, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.usuario import UsuarioCreate, LoginRequest, UsuarioRead, RefreshRequest
from app.services import auth_service
from app.models.usuario import Usuario
from app.core.config import settings
from app.core.rate_limit import login_limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


def _set_token_cookie(response: Response, token: str, max_age_seconds: int) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=max_age_seconds,
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )


def _set_refresh_cookie(response: Response, token: str, max_age_seconds: int) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        max_age=max_age_seconds,
        domain=settings.COOKIE_DOMAIN,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/api/v1/auth",
    )


def _check_login_rate_limit(request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    if not login_limiter.is_allowed(ip):
        raise HTTPException(
            status_code=429,
            detail="Demasiados intentos. Intente de nuevo en 15 minutos.",
        )
    return ip


def _usuario_to_userpublic(usuario: Usuario) -> dict:

    return {
        "id": usuario.id,
        "email": usuario.email,
        "full_name": f"{usuario.nombre} {usuario.apellido or ''}".strip(),
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "celular": usuario.celular,
        "is_active": getattr(usuario, "deleted_at", None) is None,
        "roles": [usuario.rol.upper()],
    }


@router.post("/register")
def register(data: UsuarioCreate, response: Response, request: Request):
    ip = _check_login_rate_limit(request)
    access_token, refresh_token, usuario = auth_service.register_user(data, ip)
    _set_token_cookie(response, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    _set_refresh_cookie(response, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    return {
        "usuario": _usuario_to_userpublic(usuario),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/login")
def login(data: LoginRequest, response: Response, request: Request):
    ip = _check_login_rate_limit(request)
    access_token, refresh_token, usuario = auth_service.login_user(data, ip)
    _set_token_cookie(response, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    _set_refresh_cookie(response, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    return {
        "usuario": _usuario_to_userpublic(usuario),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/token")
def login_token(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None, request: Request = None):
    ip = _check_login_rate_limit(request)
    login_data = LoginRequest(email=form_data.username, password=form_data.password)
    access_token, refresh_token, usuario = auth_service.login_user(login_data, ip)
    _set_token_cookie(response, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    _set_refresh_cookie(response, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh(response: Response, request: Request, body: RefreshRequest | None = None):
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str and body:
        refresh_token_str = body.refresh_token
    if not refresh_token_str:
        raise HTTPException(status_code=400, detail="Refresh token requerido")

    access_token, new_refresh_token, usuario = auth_service.refresh_user_token(refresh_token_str)
    _set_token_cookie(response, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    _set_refresh_cookie(response, new_refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    return {
        "usuario": _usuario_to_userpublic(usuario),
        "access_token": access_token,
        "refresh_token": new_refresh_token,
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/", domain=settings.COOKIE_DOMAIN, secure=settings.COOKIE_SECURE, samesite=settings.COOKIE_SAMESITE)
    response.delete_cookie(key="refresh_token", path="/api/v1/auth", domain=settings.COOKIE_DOMAIN, secure=settings.COOKIE_SECURE, samesite=settings.COOKIE_SAMESITE)
    return {"message": "Sesión cerrada"}


@router.get("/me")
def me(usuario: Usuario = Depends(auth_service.get_current_user)):

    return _usuario_to_userpublic(usuario)