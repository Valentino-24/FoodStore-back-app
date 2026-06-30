"""Seed data obligatorio — especificación v6.0 sección 14.2.

Ejecutado al iniciar la aplicación (lifespan en main.py).
Idempotente: solo inserta registros que no existen.
"""

from sqlmodel import select

from app.core.security import hash_password
from app.core.uow import UnitOfWork
from app.models.rol import Rol
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.unidad_medida import UnidadMedida
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.producto import Producto


def seed_all():
    """Ejecuta todo el seed en una transacción."""
    with UnitOfWork() as uow:
        _seed_roles(uow)
        _seed_estados_pedido(uow)
        _seed_formas_pago(uow)
        _seed_unidades_medida(uow)
        _seed_admin_user(uow)
        _seed_demo_data(uow)


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


def _seed_demo_data(uow: UnitOfWork):
    """Seed de datos demo: categorías, ingredientes y productos.
    Idempotente — solo inserta si no existen (chequea por nombre)."""

    # ── Categorías ────────────────────────────────────────────────────
    categorias_data = [
        {"nombre": "Hamburguesas", "descripcion": "Hamburguesas clásicas y especiales"},
        {"nombre": "Pizzas", "descripcion": "Pizzas artesanales al horno"},
        {"nombre": "Bebidas", "descripcion": "Gaseosas, aguas y jugos"},
        {"nombre": "Postres", "descripcion": "Helados, tortas y más"},
        {"nombre": "Ensaladas", "descripcion": "Frescas y saludables"},
        {"nombre": "Acompañantes", "descripcion": "Papas, aros de cebolla y guarniciones"},
    ]
    categorias = {}
    for c in categorias_data:
        existing = uow.session.exec(
            select(Categoria).where(Categoria.nombre == c["nombre"])
        ).first()
        if existing:
            categorias[c["nombre"]] = existing
        else:
            cat = Categoria(**c)
            uow.session.add(cat)
            uow.session.flush()
            uow.session.refresh(cat)
            categorias[c["nombre"]] = cat

    # ── Ingredientes ──────────────────────────────────────────────────
    ingredientes_data = [
        {"nombre": "Carne vacuna", "descripcion": "Medallón de carne 100% vacuna", "stock_cantidad": 100},
        {"nombre": "Queso cheddar", "descripcion": "Fetas de cheddar madurado", "stock_cantidad": 80},
        {"nombre": "Queso mozzarella", "descripcion": "Mozzarella hilada", "stock_cantidad": 60},
        {"nombre": "Lechuga", "descripcion": "Lechuga fresca criolla", "stock_cantidad": 40},
        {"nombre": "Tomate", "descripcion": "Tomate perita fresco", "stock_cantidad": 50},
        {"nombre": "Cebolla", "descripcion": "Cebolla morada", "stock_cantidad": 45},
        {"nombre": "Pan de hamburguesa", "descripcion": "Pan brioche con sésamo", "stock_cantidad": 90},
        {"nombre": "Panceta", "descripcion": "Panceta ahumada", "stock_cantidad": 30},
        {"nombre": "Huevo", "descripcion": "Huevo de campo", "stock_cantidad": 60},
        {"nombre": "Pepperoni", "descripcion": "Rodajas de pepperoni", "stock_cantidad": 40},
        {"nombre": "Salsa de tomate", "descripcion": "Salsa pomodoro artesanal", "stock_cantidad": 50},
        {"nombre": "Masa de pizza", "descripcion": "Masa fina a la piedra", "stock_cantidad": 35},
        {"nombre": "Pollo", "descripcion": "Pechuga de pollo grillada", "stock_cantidad": 25},
        {"nombre": "Chocolate", "descripcion": "Chocolate semi-amargo", "stock_cantidad": 20},
        {"nombre": "Papa", "descripcion": "Papa blanca", "stock_cantidad": 200},
        {"nombre": "Helado de vainilla", "descripcion": "Helado artesanal de vainilla", "stock_cantidad": 30},
        {"nombre": "Dulce de leche", "descripcion": "Dulce de leche repostero", "stock_cantidad": 15},
        {"nombre": "Rúcula", "descripcion": "Rúcula fresca", "stock_cantidad": 10},
        {"nombre": "Crutones", "descripcion": "Crutones de pan tostado", "stock_cantidad": 20},
        {"nombre": "Queso parmesano", "descripcion": "Parmesano en lascas", "stock_cantidad": 12},
    ]
    ingredientes = {}
    for i in ingredientes_data:
        existing = uow.session.exec(
            select(Ingrediente).where(Ingrediente.nombre == i["nombre"])
        ).first()
        if existing:
            ingredientes[i["nombre"]] = existing
        else:
            ing = Ingrediente(**i)
            uow.session.add(ing)
            uow.session.flush()
            uow.session.refresh(ing)
            ingredientes[i["nombre"]] = ing

    # ── Unidades de medida (referencias) ──────────────────────────────
    def _get_unidad(simbolo: str):
        return uow.unidades_medida.get_by_simbolo(simbolo)

    # ── Productos ─────────────────────────────────────────────────────
    productos_data = [
        {
            "nombre": "Hamburguesa Clásica",
            "descripcion": "Medallón de carne, lechuga, tomate y cebolla en pan brioche",
            "precio_base": 4500.00,
            "stock_cantidad": 50,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Hamburguesas"],
            "ingredientes": [
                ("Carne vacuna", "ud", 1.0, False),
                ("Lechuga", "g", 30.0, True),
                ("Tomate", "g", 40.0, True),
                ("Cebolla", "g", 20.0, True),
                ("Pan de hamburguesa", "ud", 1.0, False),
            ],
        },
        {
            "nombre": "Cheeseburger",
            "descripcion": "Doble medallón con cheddar, panceta y huevo",
            "precio_base": 6200.00,
            "stock_cantidad": 40,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Hamburguesas"],
            "ingredientes": [
                ("Carne vacuna", "ud", 2.0, False),
                ("Queso cheddar", "ud", 2.0, False),
                ("Panceta", "ud", 2.0, True),
                ("Huevo", "ud", 1.0, True),
                ("Pan de hamburguesa", "ud", 1.0, False),
            ],
        },
        {
            "nombre": "Hamburguesa Veggie",
            "descripcion": "Medallón de lentejas, rúcula, tomate y cebolla caramelizada",
            "precio_base": 5100.00,
            "stock_cantidad": 25,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Hamburguesas"],
            "ingredientes": [
                ("Lechuga", "g", 30.0, False),
                ("Tomate", "g", 40.0, False),
                ("Cebolla", "g", 30.0, False),
                ("Pan de hamburguesa", "ud", 1.0, False),
            ],
        },
        {
            "nombre": "Pizza Margherita",
            "descripcion": "Salsa de tomate, mozzarella fresca y albahaca",
            "precio_base": 5800.00,
            "stock_cantidad": 30,
            "disponible": True,
            "unidad_venta_simbolo": "porc",
            "categorias": ["Pizzas"],
            "ingredientes": [
                ("Salsa de tomate", "ml", 100.0, False),
                ("Queso mozzarella", "g", 150.0, False),
                ("Masa de pizza", "ud", 1.0, False),
            ],
        },
        {
            "nombre": "Pizza Pepperoni",
            "descripcion": "Salsa de tomate, mozzarella y pepperoni",
            "precio_base": 6500.00,
            "stock_cantidad": 25,
            "disponible": True,
            "unidad_venta_simbolo": "porc",
            "categorias": ["Pizzas"],
            "ingredientes": [
                ("Salsa de tomate", "ml", 100.0, False),
                ("Queso mozzarella", "g", 150.0, False),
                ("Pepperoni", "ud", 15.0, False),
                ("Masa de pizza", "ud", 1.0, False),
            ],
        },
        {
            "nombre": "Pizza Cuatro Quesos",
            "descripcion": "Mozzarella, parmesano, cheddar y azul",
            "precio_base": 7200.00,
            "stock_cantidad": 20,
            "disponible": True,
            "unidad_venta_simbolo": "porc",
            "categorias": ["Pizzas"],
            "ingredientes": [
                ("Salsa de tomate", "ml", 80.0, False),
                ("Queso mozzarella", "g", 120.0, False),
                ("Queso parmesano", "g", 50.0, False),
                ("Queso cheddar", "ud", 2.0, False),
                ("Masa de pizza", "ud", 1.0, False),
            ],
        },
        {
            "nombre": "Coca-Cola 500ml",
            "descripcion": "Lata de Coca-Cola original 500ml",
            "precio_base": 1200.00,
            "stock_cantidad": 200,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Bebidas"],
            "ingredientes": [],
        },
        {
            "nombre": "Agua Mineral 500ml",
            "descripcion": "Agua mineral sin gas",
            "precio_base": 900.00,
            "stock_cantidad": 150,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Bebidas"],
            "ingredientes": [],
        },
        {
            "nombre": "Limonada Natural",
            "descripcion": "Limonada recién exprimida con menta",
            "precio_base": 1500.00,
            "stock_cantidad": 60,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Bebidas"],
            "ingredientes": [],
        },
        {
            "nombre": "Helado de Chocolate",
            "descripcion": "Dos bochas de helado artesanal con salsa de chocolate",
            "precio_base": 2800.00,
            "stock_cantidad": 40,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Postres"],
            "ingredientes": [
                ("Chocolate", "g", 60.0, False),
                ("Helado de vainilla", "ud", 2.0, False),
            ],
        },
        {
            "nombre": "Brownie con Helado",
            "descripcion": "Brownie caliente con helado de vainilla y dulce de leche",
            "precio_base": 3500.00,
            "stock_cantidad": 30,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Postres"],
            "ingredientes": [
                ("Chocolate", "g", 80.0, False),
                ("Helado de vainilla", "ud", 1.0, False),
                ("Dulce de leche", "g", 40.0, False),
            ],
        },
        {
            "nombre": "Ensalada César",
            "descripcion": "Lechuga, pollo grillado, crutones y parmesano",
            "precio_base": 4200.00,
            "stock_cantidad": 20,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Ensaladas"],
            "ingredientes": [
                ("Lechuga", "g", 100.0, False),
                ("Pollo", "ud", 1.0, False),
                ("Crutones", "g", 30.0, False),
                ("Queso parmesano", "g", 30.0, False),
            ],
        },
        {
            "nombre": "Ensalada Caprese",
            "descripcion": "Tomate, mozzarella fresca y albahaca",
            "precio_base": 3800.00,
            "stock_cantidad": 15,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Ensaladas"],
            "ingredientes": [
                ("Tomate", "g", 150.0, False),
                ("Queso mozzarella", "g", 100.0, False),
                ("Rúcula", "g", 30.0, True),
            ],
        },
        {
            "nombre": "Papas Fritas Grandes",
            "descripcion": "Papas fritas crocantes con sal marina",
            "precio_base": 2500.00,
            "stock_cantidad": 100,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Acompañantes"],
            "ingredientes": [
                ("Papa", "g", 300.0, False),
            ],
        },
        {
            "nombre": "Aros de Cebolla",
            "descripcion": "Aros de cebolla empanizados y fritos",
            "precio_base": 2200.00,
            "stock_cantidad": 50,
            "disponible": True,
            "unidad_venta_simbolo": "ud",
            "categorias": ["Acompañantes"],
            "ingredientes": [
                ("Cebolla", "g", 200.0, False),
            ],
        },
    ]

    # Saltar si ya hay productos demo (chequea por el primero)
    existing_count = uow.session.exec(
        select(Producto)
    ).first()
    if existing_count and uow.session.exec(
        select(Producto).where(Producto.nombre == "Hamburguesa Clásica")
    ).first():
        return  # Ya está seedeado

    for pdata in productos_data:
        unidad = _get_unidad(pdata["unidad_venta_simbolo"])
        producto = Producto(
            nombre=pdata["nombre"],
            descripcion=pdata["descripcion"],
            precio_base=pdata["precio_base"],
            stock_cantidad=pdata["stock_cantidad"],
            disponible=pdata["disponible"],
            unidad_venta_id=unidad.id if unidad else None,
        )
        uow.session.add(producto)
        uow.session.flush()
        uow.session.refresh(producto)

        # Relaciones con categorías
        for cat_nombre in pdata["categorias"]:
            cat = categorias.get(cat_nombre)
            if cat:
                uow.productos_categoria.add_relation(
                    producto_id=producto.id,
                    categoria_id=cat.id,
                    es_principal=True,
                )

        # Relaciones con ingredientes
        for ing_nombre, unidad_simbolo, cantidad, es_removible in pdata["ingredientes"]:
            ing = ingredientes.get(ing_nombre)
            uni_ing = _get_unidad(unidad_simbolo) if unidad_simbolo else None
            if ing:
                uow.productos_ingrediente.add_relation(
                    producto_id=producto.id,
                    ingrediente_id=ing.id,
                    es_removible=es_removible,
                    cantidad=cantidad,
                    unidad_medida_id=uni_ing.id if uni_ing else None,
                )
