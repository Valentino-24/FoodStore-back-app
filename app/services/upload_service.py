import cloudinary.uploader
import cloudinary.api
from fastapi import HTTPException, UploadFile

from app.core.config import settings
import app.core.cloudinary_config  # noqa: F401 — ensure configured on import


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _validate_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}. "
                   f"Permitidos: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )
    # Read first bytes to check size (content-length may not be set)
    # We'll check after upload, but do a quick pre-check
    if not settings.CLOUDINARY_CLOUD_NAME:
        raise HTTPException(status_code=500, detail="Cloudinary no configurado")


async def upload_imagen(file: UploadFile) -> dict:
    _validate_file(file)

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Máximo {MAX_FILE_SIZE // (1024*1024)} MB",
        )

    try:
        result = cloudinary.uploader.upload(
            contents,
            folder=settings.CLOUDINARY_UPLOAD_FOLDER,
            resource_type="image",
            use_filename=True,
            unique_filename=True,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al subir a Cloudinary: {str(e)}")

    return {
        "secure_url": result["secure_url"],
        "public_id": result["public_id"],
        "width": result.get("width"),
        "height": result.get("height"),
        "format": result.get("format"),
        "resource_type": result.get("resource_type"),
    }


def eliminar_imagen(public_id: str) -> dict:
    try:
        result = cloudinary.uploader.destroy(public_id)
        if result.get("result") != "ok":
            raise HTTPException(
                status_code=404,
                detail=f"No se pudo eliminar la imagen: {result.get('result')}",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al eliminar de Cloudinary: {str(e)}")

    return {"ok": True, "public_id": public_id}
