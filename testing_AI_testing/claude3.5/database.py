from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# from dotenv import load_dotenv

load_dotenv()

## originally used dotenv
## DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./library.db")
DATABASE_URL = os.environ("LIBRARY_DB_URL", "sqlite:///./library.db")

# Create SQLAlchemy engine
if DATABASE_URL == "sqlite:///./library.db":
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()