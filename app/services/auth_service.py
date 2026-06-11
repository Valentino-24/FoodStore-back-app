from sqlmodel import select

from fastapi import HTTPException, Request

from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.uow import UnitOfWork
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.models.rol import Rol
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
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

def register_user(data: UsuarioCreate) -> tuple[str, UsuarioRead]:
    with UnitOfWork() as uow:
        existing = uow.usuarios.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        usuario = Usuario(
            email=data.email,
            hashed_password=hash_password(data.password),
            nombre=data.nombre,
            rol="CLIENT",
        )
        uow.usuarios.create(usuario)

        rol_client = uow.roles.get_by_codigo("CLIENT")
        if rol_client:
            uow.session.add(UsuarioRol(usuario_id=usuario.id, rol_id=rol_client.id))
            uow.commit()

        access_token = create_access_token({"sub": usuario.email})
        usuario_read = UsuarioRead(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            rol=usuario.rol,
        )
        return access_token, usuario_read

def login_user(data: LoginRequest) -> tuple[str, UsuarioRead]:
    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_email(data.email)
        if not usuario or not verify_password(data.password, usuario.hashed_password):
            raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

        access_token = create_access_token({"sub": usuario.email})
        usuario_read = UsuarioRead(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            rol=usuario.rol,
        )
        return access_token, usuario_read

def seed_admin():

    with UnitOfWork() as uow:
        _seed_roles(uow)
        _seed_estados_pedido(uow)
        _seed_formas_pago(uow)
        _seed_admin_user(uow)
        uow.commit()

def _seed_roles(uow: UnitOfWork):
    roles_data = [
        {"codigo": "ADMIN", "nombre": "Administrador", "descripcion": "CRUD completo de todo el sistema"},
        {"codigo": "STOCK", "nombre": "Gestor de Stock", "descripcion": "Leer productos, actualizar stock y disponibilidad"},
        {"codigo": "PEDIDOS", "nombre": "Gestor de Pedidos", "descripcion": "Ver y avanzar estados de pedidos"},
        {"codigo": "CLIENT", "nombre": "Cliente", "descripcion": "Catálogo, carrito, pedidos propios"},
    ]
    for r in roles_data:
        existing = uow.roles.get_by_codigo(r["codigo"])
        if not existing:
            uow.session.add(Rol(**r))

def _seed_estados_pedido(uow: UnitOfWork):
    estados_data = [
        {"codigo": "PENDIENTE", "nombre": "Pendiente", "orden": 10},
        {"codigo": "CONFIRMADO", "nombre": "Confirmado", "orden": 20},
        {"codigo": "EN_PREP", "nombre": "En Preparación", "orden": 30},
        {"codigo": "EN_CAMINO", "nombre": "En Camino", "orden": 40},
        {"codigo": "ENTREGADO", "nombre": "Entregado", "orden": 50},
        {"codigo": "CANCELADO", "nombre": "Cancelado", "orden": 60},
    ]
    for e in estados_data:
        existing = uow.session.exec(
            select(EstadoPedido).where(EstadoPedido.codigo == e["codigo"])
        ).first()
        if not existing:
            uow.session.add(EstadoPedido(**e))

def _seed_formas_pago(uow: UnitOfWork):
    formas_data = [
        {"codigo": "EFECTIVO", "nombre": "Efectivo"},
        {"codigo": "TARJETA_CREDITO", "nombre": "Tarjeta de Crédito"},
        {"codigo": "TARJETA_DEBITO", "nombre": "Tarjeta de Débito"},
        {"codigo": "TRANSFERENCIA", "nombre": "Transferencia Bancaria"},
    ]
    for f in formas_data:
        existing = uow.session.exec(
            select(FormaPago).where(FormaPago.codigo == f["codigo"])
        ).first()
        if not existing:
            uow.session.add(FormaPago(**f))

def _seed_admin_user(uow: UnitOfWork):
    admin = uow.usuarios.get_by_email("admin@gmail.com")
    if admin:
        return

    usuario = Usuario(
        email="admin@gmail.com",
        hashed_password=hash_password("admin1234"),
        nombre="Admin",
        rol="ADMIN",
    )
    uow.usuarios.create(usuario)

    rol_admin = uow.roles.get_by_codigo("ADMIN")
    if rol_admin:
        uow.session.add(UsuarioRol(usuario_id=usuario.id, rol_id=rol_admin.id))