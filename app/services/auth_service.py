from fastapi import HTTPException, Request

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_access_token
from app.core.rate_limit import login_limiter
from app.core.uow import UnitOfWork
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.schemas.usuario import UsuarioCreate, LoginRequest, UsuarioRead
from app.models.unidad_medida import UnidadMedida

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

def register_user(data: UsuarioCreate, ip: str | None = None) -> tuple[str, str, UsuarioRead]:
    with UnitOfWork() as uow:
        existing = uow.usuarios.get_by_email(data.email)
        if existing:
            if ip:
                login_limiter.record_failure(ip)
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
            uow.commit()

        if ip:
            login_limiter.reset(ip)

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

def login_user(data: LoginRequest, ip: str | None = None) -> tuple[str, str, UsuarioRead]:
    with UnitOfWork() as uow:
        usuario = uow.usuarios.get_by_email(data.email)
        if not usuario or not verify_password(data.password, usuario.hashed_password):
            if ip:
                login_limiter.record_failure(ip)
            raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

        if ip:
            login_limiter.reset(ip)

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


def seed_admin():

    with UnitOfWork() as uow:
        _seed_roles(uow)
        _seed_estados_pedido(uow)
        _seed_formas_pago(uow)
        _seed_unidades_medida(uow)
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
            uow.roles.create(Rol(**r))

def _seed_estados_pedido(uow: UnitOfWork):
    estados_data = [
        {"codigo": "PENDIENTE", "nombre": "Pendiente", "orden": 10, "es_terminal": False},
        {"codigo": "CONFIRMADO", "nombre": "Confirmado", "orden": 20, "es_terminal": False},
        {"codigo": "EN_PREP", "nombre": "En Preparación", "orden": 30, "es_terminal": False},
        {"codigo": "ENTREGADO", "nombre": "Entregado", "orden": 40, "es_terminal": True},
        {"codigo": "CANCELADO", "nombre": "Cancelado", "orden": 50, "es_terminal": True},
    ]
    for e in estados_data:
        existing = uow.estados_pedido.get_by_codigo(e["codigo"])
        if not existing:
            uow.estados_pedido.create(EstadoPedido(**e))
        elif existing.es_terminal is None:
            existing.es_terminal = e["es_terminal"]
            uow.estados_pedido.update(existing)

def _seed_formas_pago(uow: UnitOfWork):
    formas_data = [
        {"codigo": "EFECTIVO", "nombre": "Efectivo"},
        {"codigo": "TARJETA_CREDITO", "nombre": "Tarjeta de Crédito"},
        {"codigo": "TARJETA_DEBITO", "nombre": "Tarjeta de Débito"},
        {"codigo": "TRANSFERENCIA", "nombre": "Transferencia Bancaria"},
        {"codigo": "MERCADOPAGO", "nombre": "Mercado Pago"},
    ]
    for f in formas_data:
        existing = uow.formas_pago.get_by_codigo(f["codigo"])
        if not existing:
            uow.formas_pago.create(FormaPago(**f))

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
        uow.usuarios_roles.add_role(usuario_id=usuario.id, rol_id=rol_admin.id)


def _seed_unidades_medida(uow: UnitOfWork):
    unidades_data = [
        {"nombre": "kilogramo", "simbolo": "kg", "tipo": "peso"},
        {"nombre": "gramo", "simbolo": "g", "tipo": "peso"},
        {"nombre": "litro", "simbolo": "L", "tipo": "volumen"},
        {"nombre": "mililitro", "simbolo": "ml", "tipo": "volumen"},
        {"nombre": "unidad", "simbolo": "ud", "tipo": "contable"},
        {"nombre": "porciones", "simbolo": "porc", "tipo": "contable"},
    ]
    for u in unidades_data:
        existing = uow.unidades_medida.get_by_simbolo(u["simbolo"])
        if not existing:
            uow.unidades_medida.create(UnidadMedida(**u))