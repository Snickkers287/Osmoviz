from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
DB_Path = Path(__file__).resolve().parent.parent / "osmoviz.db"

engine = create_engine(f"sqlite:///{DB_Path}", connect_args={"check_same_thread": False},)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase): pass
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def init_db():
    from backend import models
    Base.metadata.create_all(bind=engine)
