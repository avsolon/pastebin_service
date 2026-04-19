from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from app.config import QR_DIR

router = APIRouter()


@router.get("/qr/{code}.png")
def get_qr(code: str):
    path = os.path.join(QR_DIR, f"{code}.png")

    if not os.path.exists(path):
        raise HTTPException(404)

    return FileResponse(path)