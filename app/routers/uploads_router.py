from fastapi import APIRouter, Depends, UploadFile, File

from app.models.usuario import Usuario
from app.services import upload_service
from app.core.dependencies import require_admin

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/imagen")
async def subir_imagen(
    file: UploadFile = File(...),
    _: Usuario = Depends(require_admin),
):
    return await upload_service.upload_imagen(file)


@router.delete("/imagen/{public_id:path}")
def eliminar_imagen(
    public_id: str,
    _: Usuario = Depends(require_admin),
):
    return upload_service.eliminar_imagen(public_id)
