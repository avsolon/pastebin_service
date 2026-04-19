from fastapi import FastAPI
from app.db.database import Base, engine
from app.routes import paste, qr

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(paste.router)
app.include_router(qr.router)