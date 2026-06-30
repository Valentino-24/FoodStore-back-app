from fastapi import HTTPException, Request

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_access_token
from app.core.uow import UnitOfWork
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, LoginRequest, UsuarioRead

def get_current_user(request: Request) -> Usuario:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No autenticado")

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido")

    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_email(email)
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        return usuario

def register_user(data: UsuarioCreate) -> tuple[str, str, UsuarioRead]:
    with UnitOfWork() as uow:
        existing = uow.usuarios.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        usuario = Usuario(
            email=data.email,
            hashed_password=hash_password(data.password),
            nombre=data.nombre,
            apellido=data.apellido,
            celular=data.celular,
            rol="CLIENT",
        )
        uow.usuarios.create(usuario)

        rol_client = uow.roles.get_by_codigo("CLIENT")
        if rol_client:
            uow.usuarios_roles.add_role(usuario_id=usuario.id, rol_id=rol_client.id)

        access_token = create_access_token({"sub": usuario.email})
        refresh_token = create_refresh_token({"sub": usuario.email})
        usuario_read = UsuarioRead(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            celular=usuario.celular,
            rol=usuario.rol,
        )
        return access_token, refresh_token, usuario_read

def login_user(data: LoginRequest) -> tuple[str, str, UsuarioRead]:
    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_email(data.email)
        if not usuario or not verify_password(data.password, usuario.hashed_password):
            raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

        access_token = create_access_token({"sub": usuario.email})
        refresh_token = create_refresh_token({"sub": usuario.email})
        usuario_read = UsuarioRead(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            celular=usuario.celular,
            rol=usuario.rol,
        )
        return access_token, refresh_token, usuario_read

def refresh_user_token(refresh_token_str: str) -> tuple[str, str, UsuarioRead]:
    payload = decode_access_token(refresh_token_str)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido")

    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_email(email)
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        access_token = create_access_token({"sub": usuario.email})
        refresh_token = create_refresh_token({"sub": usuario.email})
        usuario_read = UsuarioRead(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            celular=usuario.celular,
            rol=usuario.rol,
        )
        return access_token, refresh_token, usuario_read