from pydantic import BaseModel

class URLRequest(BaseModel):
    long_url: str

class URLResponse(BaseModel):
    short_url: str
