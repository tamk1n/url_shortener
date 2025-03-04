from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import redis
from app import schemas, crud, database, cache
import hashlib
import base64

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    return cache.redis_client

def encode_id(url: str) -> str:
    hash_object = hashlib.md5(url.encode())
    return base64.urlsafe_b64encode(hash_object.digest())[:6].decode()

@router.post("/shorten", response_model=schemas.URLResponse)
def shorten_url(url_data: schemas.URLRequest, db: Session = Depends(get_db), r: redis.Redis = Depends(get_redis)):
    existing = crud.get_by_long_url(db, url_data.long_url)
    if existing:
        return {"short_id": existing.short_id}

    short_id = encode_id(url_data.long_url)
    db_entry = crud.create_url(db, url_data.long_url, short_id)
    r.set(short_id, url_data.long_url)  # Cache in Redis
    return {"short_id": short_id}

@router.get("/{short_id}")
def redirect_url(short_id: str, db: Session = Depends(get_db), r: redis.Redis = Depends(get_redis)):
    cached_url = r.get(short_id)
    if cached_url:
        return {"long_url": cached_url.decode()}

    db_entry = crud.get_by_short_id(db, short_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    r.set(short_id, db_entry.long_url)
    return {"long_url": db_entry.long_url}
