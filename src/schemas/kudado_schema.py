from pydantic import BaseModel
from typing import Optional, List

class SchemaDates(BaseModel):
    start: int
    end: int

class SchemaSource(BaseModel):
    name: Optional[str] = None
    link: Optional[str] = None

class SchemaImages(BaseModel):
    image: str
    source: SchemaSource

class SchemaPlace(BaseModel):
    id: Optional[int] = None

class SchemaEvent(BaseModel):
    dates: List[SchemaDates]
    description: str
    images: List[SchemaImages]
    place: Optional[SchemaPlace] = None
    title: str
    price: Optional[str] = None
    
class SchemaEventValidator(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[SchemaEvent]
