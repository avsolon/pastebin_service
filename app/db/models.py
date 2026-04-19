from sqlalchemy import Column, String, DateTime
from .database import Base


class Paste(Base):
    __tablename__ = "pastes"

    code = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    qr_path = Column(String, nullable=True)
    created_at = Column(DateTime)