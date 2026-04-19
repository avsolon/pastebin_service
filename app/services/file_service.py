import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException
from app.config import *


def check_file_size(file: UploadFile):
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if file.content_type.startswith("image"):
        if size > MAX_IMAGE_SIZE:
            raise HTTPException(400, "Image too large")
    elif file.content_type.startswith("video"):
        if size > MAX_VIDEO_SIZE:
            raise HTTPException(400, "Video too large")
    else:
        if size > MAX_FILE_SIZE:
            raise HTTPException(400, "File too large")


def save_file(file: UploadFile):
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return path


def delete_file(path: str):
    if path and os.path.exists(path):
        os.remove(path)