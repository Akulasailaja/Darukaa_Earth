import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Example: postgresql://user:password@localhost:5432/darukaa
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://darukaa_user:darukaa_pass@localhost:5432/darukaa_db",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
