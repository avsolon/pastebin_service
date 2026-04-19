import uuid
from datetime import datetime, timedelta
from app.config import EXPIRE_MINUTES


def generate_code():
    return uuid.uuid4().hex


def is_expired(paste):
    return datetime.utcnow() > paste.created_at + timedelta(minutes=EXPIRE_MINUTES)