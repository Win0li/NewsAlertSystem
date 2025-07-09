from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.models import User
from app.database import SessionLocal, KEYWORDS

router = APIRouter()


@router.post("/create_user")
def create_user(email:EmailStr):
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            raise HTTPException(status_code=409, detail="User already exists")

        new_user = User(email=email, keywords=KEYWORDS)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    finally:
        db.close()

@router.delete("/delete_user/{email}")
def delete_user(email: EmailStr):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"message": f"{email} deleted"}
    finally:
        db.close()