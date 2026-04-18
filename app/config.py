import os

BASE_URL = "https://domain.com"

UPLOAD_DIR = "uploads"
QR_DIR = "qr"

EXPIRE_MINUTES = 60

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_VIDEO_SIZE = 20 * 1024 * 1024
MAX_FILE_SIZE = 10 * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)