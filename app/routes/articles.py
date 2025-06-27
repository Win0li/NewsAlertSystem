from fastapi import APIRouter
from app.models import Article
from app.database import SessionLocal

router = APIRouter()

@router.get("/articles")
def get_articles(keyword: ):
    db = SessionLocal()
    try:
        if keyword:
            return db.query(Article).filter_by(keyword=keyword).all()
        return db.query(Article).all()
    finally:
        db.close()

@router.get("/status")
def status():
    return {"status": "ok"}


