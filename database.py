from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from dotenv import load_dotenv
import os       
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class FileRecord(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    file_name = Column(String)
    s3_url = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_file_record(user_id, file_name, s3_url):
    db = SessionLocal()
    record = FileRecord(
        id=str(uuid.uuid4()),
        user_id=user_id,
        file_name=file_name,
        s3_url=s3_url
    )
    db.add(record)
    db.commit()
    db.close()