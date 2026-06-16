from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel

class EstadoPedidoRead(SQLModel):
    id: int
    codigo: str
    nombre: str
    orden: int
    es_terminal: bool = False

class FormaPagoRead(SQLModel):
    id: int
    nombre: str
    codigo: str

class DetallePedidoCreate(SQLModel):
    producto_id: int
    cantidad: int
    personalizacion: Optional[List[int]] = None

class DetallePedidoRead(SQLModel):
    id: int
    producto_id: int
    nombre_producto: str
    precio_unitario: float
    cantidad: int
    subtotal: float
    subtotal_snap: float = 0.0
    personalizacion: Optional[List[int]] = None

class PedidoCreate(SQLModel):
    forma_pago_id: int
    direccion_entrega_id: Optional[int] = None
    descuento: float = 0.0
    costo_envio: float = 50.0
    detalles: List[DetallePedidoCreate]

class PedidoRead(SQLModel):
    id: int
    usuario_id: int
    fecha_pedido: datetime
    estado_actual_id: int
    forma_pago_id: int
    direccion_entrega_id: Optional[int] = None
    subtotal: float = 0.0
    descuento: float = 0.0
    costo_envio: float = 50.0
    total: float

    detalles: List[DetallePedidoRead] = []
    estado_actual: Optional[EstadoPedidoRead] = None
    forma_pago: Optional[FormaPagoRead] = None

class PedidoReadSimple(SQLModel):

    id: int
    usuario_id: int
    fecha_pedido: datetime
    estado_actual_id: int
    forma_pago_id: int
    subtotal: float = 0.0
    descuento: float = 0.0
    costo_envio: float = 50.0
    total: float

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

class CambioEstadoRequest(SQLModel):
    nuevo_estado_id: int
    observacion: Optional[str] = None