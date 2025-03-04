from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import redis
import base64
import hashlib
from app import models, schemas, crud, database, cache
from .database import engine
from dotenv import load_dotenv
import os

load_dotenv()  # Ensure that the .env file is loaded

DATABASE_URL = os.getenv("DATABASE_URL")
ROOT_URL = os.getenv("ROOT_URL", "http://localhost:8000")  # Default to localhost if not set

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for DB Session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for Redis
def get_redis():
    return cache.redis_client

# Base62 encoding
def encode_id(url: str) -> str:
    hash_object = hashlib.md5(url.encode())
    return base64.urlsafe_b64encode(hash_object.digest())[:6].decode()

@app.post("/shorten", response_model=schemas.URLResponse)
def shorten_url(url_data: schemas.URLRequest, db: Session = Depends(get_db), r: redis.Redis = Depends(get_redis)):
    """ Shortens a long URL. """
    existing = crud.get_by_long_url(db, url_data.long_url)
    print(existing)
    if existing:
        return {"short_url": f"{ROOT_URL}/{existing.short_id}"}  # Return full URL
    
    short_id = encode_id(url_data.long_url)
    db_entry = crud.create_url(db, url_data.long_url, short_id)
    r.set(short_id, url_data.long_url)  # Cache in Redis
    return {"short_url": f"{ROOT_URL}/{short_id}"}  # Return full URL


@app.get("/{short_id}")
def redirect_url(short_id: str, db: Session = Depends(get_db), r: redis.Redis = Depends(get_redis)):
    """ Redirects from short URL to original URL. """
    cached_url = r.get(short_id)
    
    if cached_url:  # Cache hit
        return RedirectResponse(url=cached_url, status_code=302)  # Return the long URL from cache
    
    # If not in cache, check the database
    db_entry = crud.get_by_short_id(db, short_id)
    
    if not db_entry:  # If not found in the database
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    # Cache the long URL in Redis and return it
    r.set(short_id, db_entry.long_url)
    return RedirectResponse(url=db_entry.long_url, status_code=302)

