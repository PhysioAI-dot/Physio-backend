from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Der Name deiner DB, wie du ihn gerade gewählt hast
# Nutzt Environment Variable falls vorhanden (für Render), sonst SQLite lokal
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./intelaigent.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# DIESE ZEILEN SIND ESSENTIELL:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()