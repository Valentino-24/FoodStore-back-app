from fastapi import APIRouter

from app.core.uow import UnitOfWork

router = APIRouter(prefix="/formas-pago", tags=["Formas de Pago"])


@router.get("/")
def list_formas_pago():
    """Lista todos los métodos de pago habilitados (para checkout de la store app)."""
    with UnitOfWork() as uow:
        formas = uow.formas_pago.get_all_activas()
        return [
            {"id": f.id, "nombre": f.nombre, "codigo": f.codigo}
            for f in formas
        ]
