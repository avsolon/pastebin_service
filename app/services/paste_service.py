from datetime import datetime
from app.db.models import Paste
from app.utils.helpers import generate_code
from app.config import BASE_URL
from app.services.qr_service import generate_qr


def create_paste(db, text, file_path):
    code = generate_code()
    url = f"{BASE_URL}/service/pastebit/{code}"

    qr_path = generate_qr(url, code)

    paste = Paste(
        code=code,
        text=text,
        file_path=file_path,
        qr_path=qr_path,
        created_at=datetime.utcnow()
    )

    db.add(paste)
    db.commit()

    return paste, url