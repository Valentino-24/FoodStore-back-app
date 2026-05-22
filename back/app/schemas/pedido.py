from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel


# ─── EstadoPedido ───────────────────────────────────────────────

class EstadoPedidoRead(SQLModel):
    id: int
    codigo: str
    nombre: str
    orden: int


# ─── FormaPago ──────────────────────────────────────────────────

class FormaPagoRead(SQLModel):
    id: int
    nombre: str
    codigo: str


# ─── DetallePedido ──────────────────────────────────────────────

class DetallePedidoCreate(SQLModel):
    producto_id: int
    cantidad: int


class DetallePedidoRead(SQLModel):
    id: int
    producto_id: int
    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float


# ─── Pedido ─────────────────────────────────────────────────────

class PedidoCreate(SQLModel):
    forma_pago_id: int
    direccion_entrega_id: Optional[int] = None
    detalles: List[DetallePedidoCreate]


class PedidoRead(SQLModel):
    id: int
    usuario_id: int
    fecha_pedido: datetime
    estado_actual_id: int
    forma_pago_id: int
    direccion_entrega_id: Optional[int] = None
    total: float

    detalles: List[DetallePedidoRead] = []
    estado_actual: Optional[EstadoPedidoRead] = None
    forma_pago: Optional[FormaPagoRead] = None


class PedidoReadSimple(SQLModel):
    """Versión sin relaciones anidadas para listados."""
    id: int
    usuario_id: int
    fecha_pedido: datetime
    estado_actual_id: int
    forma_pago_id: int
    total: float


# ─── HistorialEstadoPedido ──────────────────────────────────────

class HistorialEstadoPedidoRead(SQLModel):
    id: int
    pedido_id: int
    estado_anterior_id: Optional[int] = None
    estado_nuevo_id: int
    cambiado_por_id: int
    fecha_cambio: datetime
    observacion: Optional[str] = None

    estado_anterior: Optional[EstadoPedidoRead] = None
    estado_nuevo: Optional[EstadoPedidoRead] = None


# ─── Cambio de estado ───────────────────────────────────────────

class CambioEstadoRequest(SQLModel):
    nuevo_estado_id: int
    observacion: Optional[str] = None
