# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from config import sqlalchemy_database_url

import os

sqlalchemy_database_url = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://"
    f"{os.getenv('DB_USER', 'root')}:"
    f"{os.getenv('DB_PASSWORD', '020110')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '3306')}/"
    f"{os.getenv('DB_NAME', 'gdee')}"
)


engine = create_engine(sqlalchemy_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 数据库会话依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()