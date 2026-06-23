from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import uuid
import os
from .config import DATABASE_URL

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class QueryLog(Base):
    __tablename__ = "queries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), default=lambda: str(uuid.uuid4()))
    exam = Column(String(20), nullable=False)
    question = Column(Text, nullable=False)
    module_used = Column(String(20))
    response = Column(Text)
    citations_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_id = Column(String(36), ForeignKey("queries.id"))
    rating = Column(Integer)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PYQCache(Base):
    __tablename__ = "pyq_cache"
    
    id = Column(String(50), primary_key=True)
    exam = Column(String(20), nullable=False)
    year = Column(Integer)
    subject = Column(String(100))
    question_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    difficulty = Column(String(10))

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
