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
async def create(text: str = Form(None), file: UploadFile = File(None)):
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

@router.get("/service/pastebit/{code}", response_class=HTMLResponse)
def preview(code: str):
    db = SessionLocal()

    paste = db.query(Paste).filter(Paste.code == code).first()

    if not paste or is_expired(paste):
        return "<h1>❌ Недоступно или истёк срок</h1>"

    return f"""
    <html>
        <head>
            <meta charset="utf-8">
            <title>Paste</title>
            <style>
                body {{
                    font-family: Arial;
                    background:#0f172a;
                    color:white;
                    text-align:center;
                    padding:50px;
                }}
                button {{
                    padding:12px 20px;
                    border:none;
                    border-radius:8px;
                    background:#3b82f6;
                    color:white;
                    cursor:pointer;
                }}
            </style>
        </head>
        <body>

            <h2>📎 Содержимое готово</h2>

            <form method="POST" action="/service/pastebit/{code}/view">
                <button>Открыть</button>
            </form>

        </body>
    </html>
    """

@router.post("/service/pastebit/{code}/view")
def view(code: str):
    db = SessionLocal()

    paste = db.query(Paste).filter(Paste.code == code).first()

    if not paste or is_expired(paste):
        raise HTTPException(status_code=404, detail="Not found")

    # === FILE CASE ===
    if paste.file_path:

        path = paste.file_path

        if not os.path.exists(path):
            db.delete(paste)
            db.commit()
            raise HTTPException(status_code=404, detail="File missing")

        response = FileResponse(path)

        # удаляем QR и запись после отдачи
        delete_file(paste.qr_path)

        db.delete(paste)
        db.commit()

        return response

    # === TEXT CASE ===
    text = paste.text

    db.delete(paste)
    db.commit()

    return HTMLResponse(f"""
    <html>
        <body style="font-family:Arial; padding:30px;">
            <pre style="white-space:pre-wrap;">{text}</pre>
        </body>
    </html>
    """)