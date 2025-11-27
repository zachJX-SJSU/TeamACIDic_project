import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL should be something like:
# mysql+pymysql://user:password@host:3306/employees
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:abc123@localhost:3306/employees",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session per request in FastAPI endpoints.
def get_db():
    from sqlalchemy.orm import Session
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
