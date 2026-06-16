from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import create_db_and_tables
from app.routers import (
    categoria_router,
    producto_router,
    ingrediente_router,
    auth_router,
    pedido_router,
    direccion_router,
    admin_router,
    unidad_medida_router,
    pagos_router,
)
from app.services.auth_service import seed_admin

app = FastAPI(
    title="FoodStore API",
    description="API de FoodStore con autenticación, RBAC, pedidos y más",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_admin()

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(categoria_router.router, prefix="/api/v1")
app.include_router(producto_router.router, prefix="/api/v1")
app.include_router(ingrediente_router.router, prefix="/api/v1")
app.include_router(pedido_router.router, prefix="/api/v1")
app.include_router(direccion_router.router, prefix="/api/v1")
app.include_router(admin_router.router, prefix="/api/v1")
app.include_router(unidad_medida_router.router, prefix="/api/v1")
app.include_router(pagos_router.router, prefix="/api/v1")