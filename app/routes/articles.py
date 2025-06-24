from fastapi import APIRouter
from app.models import Article
from app.database import SessionLocal

router = APIRouter()
