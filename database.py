# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
import models  # ← THIS IS THE KEY LINE YOU WERE MISSING

# Fix postgres:// → postgresql:// for Render
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ← THIS LINE CREATES THE TABLES AUTOMATICALLY
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()