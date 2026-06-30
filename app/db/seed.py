"""Seed data obligatorio — especificación v6.0 sección 14.2.

Ejecutado al iniciar la aplicación (lifespan en main.py).
Idempotente: solo inserta registros que no existen.
"""

from app.core.security import hash_password
from app.core.uow import UnitOfWork
from app.models.rol import Rol
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.unidad_medida import UnidadMedida
from app.models.usuario import Usuario


def seed_all():
    """Ejecuta todo el seed en una transacción."""
    with UnitOfWork() as uow:
        _seed_roles(uow)
        _seed_estados_pedido(uow)
        _seed_formas_pago(uow)
        _seed_unidades_medida(uow)
        _seed_admin_user(uow)


def _seed_roles(uow: UnitOfWork):
    roles_data = [
        {"codigo": "ADMIN", "nombre": "Administrador",
         "descripcion": "CRUD completo de todo el sistema"},
        {"codigo": "STOCK", "nombre": "Gestor de Stock",
         "descripcion": "Leer productos, actualizar stock y disponibilidad"},
        {"codigo": "PEDIDOS", "nombre": "Gestor de Pedidos",
         "descripcion": "Ver y avanzar estados de pedidos"},
        {"codigo": "CLIENT", "nombre": "Cliente",
         "descripcion": "Catálogo, carrito, pedidos propios"},
    ]
    for r in roles_data:
        if not uow.roles.get_by_codigo(r["codigo"]):
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
        if not uow.formas_pago.get_by_codigo(f["codigo"]):
            uow.formas_pago.create(FormaPago(**f))


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
        if not uow.unidades_medida.get_by_simbolo(u["simbolo"]):
            uow.unidades_medida.create(UnidadMedida(**u))


def _seed_admin_user(uow: UnitOfWork):
    if uow.usuarios.get_by_email("admin@foodstore.com"):
        return

    usuario = Usuario(
        email="admin@foodstore.com",
        hashed_password=hash_password("Admin1234!"),
        nombre="Admin",
        apellido="FoodStore",
        rol="ADMIN",
    )
    uow.usuarios.create(usuario)

    rol_admin = uow.roles.get_by_codigo("ADMIN")
    if rol_admin:
        uow.usuarios_roles.add_role(usuario_id=usuario.id, rol_id=rol_admin.id)
