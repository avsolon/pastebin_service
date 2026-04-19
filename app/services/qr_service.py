import os
import qrcode
from app.config import QR_DIR


def generate_qr(url: str, code: str):
    path = os.path.join(QR_DIR, f"{code}.png")
    img = qrcode.make(url)
    img.save(path)
    return path