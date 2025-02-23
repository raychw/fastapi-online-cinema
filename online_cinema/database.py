from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from online_cinema.models import base

DATABASE_URL = "sqlite:///./cinema.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = base.Base


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
