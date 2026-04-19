import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from app.db.database import SessionLocal
from app.db.models import Paste
from app.services.file_service import save_file, check_file_size, delete_file
from app.services.paste_service import create_paste
from app.utils.helpers import is_expired

router = APIRouter()


@router.post("/create")
async def create(
    text: str = Form(None),
    file: UploadFile = File(None)
):
    db = SessionLocal()

    # защита от пустого запроса
    if not text and (not file or not file.filename):
        raise HTTPException(status_code=400, detail="Empty request")

    file_path = None

    # безопасная проверка файла
    if file and file.filename:
        check_file_size(file)
        file_path = save_file(file)

    paste, url = create_paste(db, text, file_path)

    return {
        "url": url,
        "qr": f"/qr/{paste.code}.png"
    }

@router.get("/service/pastebit/{code}")
def preview(code: str):
    db = SessionLocal()

    paste = db.query(Paste).filter(Paste.code == code).first()

    if not paste or is_expired(paste):
        raise HTTPException(status_code=404, detail="Not found")

    # если есть файл → отдаём информацию, а не HTML
    if paste.file_path:
        return {
            "type": "file",
            "url": f"/service/pastebit/{code}/view"
        }

    return {
        "type": "text",
        "text": paste.text
    }

@router.get("/service/pastebit/{code}/view")
def view(code: str):
    db = SessionLocal()

    paste = db.query(Paste).filter(Paste.code == code).first()

    if not paste or is_expired(paste):
        raise HTTPException(status_code=404)

    # FILE CASE
    if paste.file_path:

        path = paste.file_path

        if not os.path.exists(path):
            db.delete(paste)
            db.commit()
            raise HTTPException(status_code=404, detail="File missing")

        response = FileResponse(path)

        # удаляем ПОСЛЕ отдачи
        delete_file(paste.qr_path)

        # удаляем запись
        db.delete(paste)
        db.commit()

        return response

    # TEXT CASE
    text = paste.text

    db.delete(paste)
    db.commit()

    return HTMLResponse(f"<pre>{text}</pre>")