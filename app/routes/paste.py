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

    if not text and not file:
        raise HTTPException(400)

    file_path = None

    if file:
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
        return "<h1>Недоступно</h1>"

    return f"""
    <form method="POST" action="/service/pastebit/{code}/view">
        <button>Открыть</button>
    </form>
    """


@router.post("/service/pastebit/{code}/view")
def view(code: str):
    db = SessionLocal()
    paste = db.query(Paste).filter(Paste.code == code).first()

    if not paste or is_expired(paste):
        raise HTTPException(404)

    delete_file(paste.qr_path)

    if paste.file_path:
        path = paste.file_path
        delete_file(path)

        db.delete(paste)
        db.commit()

        return FileResponse(path)

    text = paste.text

    db.delete(paste)
    db.commit()

    return HTMLResponse(f"<pre>{text}</pre>")