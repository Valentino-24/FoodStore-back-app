from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class Pago(SQLModel, table=True):
    __tablename__ = "pago"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    monto: float
    moneda: str = "ARS"
    estado: str = Field(default="PENDIENTE")  # PENDIENTE | APROBADO | RECHAZADO | CANCELADO
    mp_preference_id: Optional[str] = Field(default=None)
    mp_payment_id: Optional[int] = Field(default=None)
    mp_status: Optional[str] = Field(default=None)  # raw status from MP
    mp_status_detail: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": datetime.now(timezone.utc)},
    )
