from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, ARRAY
from datetime import datetime

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String, unique=True)
    published_at = Column(DateTime)
    source = Column(String)   
    keyword = Column(String)
    inserted_at = Column(DateTime, default=datetime.now)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    keywords = Column(ARRAY(String))  # or normalize this into a separate Keyword table later
    created_at = Column(DateTime, default=datetime.now)




