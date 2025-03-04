from sqlalchemy import Column, String
from app.database import Base

class URL(Base):
    __tablename__ = "urls"

    short_id = Column(String(10), primary_key=True, index=True)  # Shortened URL ID
    long_url = Column(String(2048), nullable=False, index=True)  # Original long URL
