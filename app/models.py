from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String, unique=True)
    published_at = Column(DateTime)
    keyword = Column(String)
    inserted_at = Column(DateTime, default=datetime.now)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    keywords = Column(ARRAY(String))  # or normalize this into a separate Keyword table later
    created_at = Column(DateTime, default=datetime.now)
    

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind = engine)