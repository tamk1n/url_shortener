from sqlalchemy.orm import Session
from app import models

def get_by_short_id(db: Session, short_id: str):
    return db.query(models.URL).filter(models.URL.short_id == short_id).first()

def get_by_long_url(db: Session, long_url: str):
    return db.query(models.URL).filter(models.URL.long_url == long_url).first()

def create_url(db: Session, long_url: str, short_id: str):
    db_url = models.URL(short_id=short_id, long_url=long_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url
