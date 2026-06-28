import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.database import create_db_and_tables
from app.core.middleware.rate_limit_middleware import RateLimitMiddleware
from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
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
    uploads_router,
    estadisticas_router,
    ws_router,
)
from app.services.auth_service import seed_admin

app = FastAPI(
    title="FoodStore API",
    description="API de FoodStore con autenticación, RBAC, pedidos y más",
    version="2.0.0",
)

# ── Rate Limiting (runs first) ───────────────────────────────────────────
app.add_middleware(RateLimitMiddleware)

# ── CORS ─────────────────────────────────────────────────────────────────
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


# ── Request Logging Middleware ───────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every HTTP request with method, path, status and duration."""
    start = time.time()
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] -> {request.method} {request.url.path}")
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    print(f"[{ts}] <- {request.method} {request.url.path}  {response.status_code}  {duration_ms:.0f}ms")
    return response


# ── Exception Handlers (RFC 7807) ────────────────────────────────────────
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# ── Startup ──────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_admin()


# ── Routers ──────────────────────────────────────────────────────────────
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(categoria_router.router, prefix="/api/v1")
app.include_router(producto_router.router, prefix="/api/v1")
app.include_router(ingrediente_router.router, prefix="/api/v1")
app.include_router(pedido_router.router, prefix="/api/v1")
app.include_router(direccion_router.router, prefix="/api/v1")
app.include_router(admin_router.router, prefix="/api/v1")
app.include_router(unidad_medida_router.router, prefix="/api/v1")
app.include_router(pagos_router.router, prefix="/api/v1")
app.include_router(uploads_router.router, prefix="/api/v1")
app.include_router(estadisticas_router.router, prefix="/api/v1")
app.include_router(ws_router.router, prefix="/api/v1")
