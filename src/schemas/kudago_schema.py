from pydantic import BaseModel
from typing import Optional, List


class DatesModel(BaseModel):
    start: int
    end: int


class SourceModel(BaseModel):
    name: Optional[str] = None
    link: Optional[str] = None


class ImagesModel(BaseModel):
    image: str
    source: SourceModel


class PlaceId(BaseModel):
    id: Optional[int] = None


class DefaultParam(BaseModel):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None


class EventResults(BaseModel):
    dates: List[DatesModel]
    description: str
    images: List[ImagesModel]
    place: Optional[PlaceId] = None
    title: str
    price: Optional[str] = None


class GetPlacesResult(PlaceId):
    title: Optional[str] = None
    address: Optional[str] = None


class GetCollectionsResult(BaseModel):
    title: str
    site_url: str


class GetMovieListResult(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    images: List[ImagesModel]


class GetNewsResult(BaseModel):
    title: str
    description: Optional[str] = None
    images: List[ImagesModel]
    site_url: str


class SchemaGetEvents(DefaultParam):
    results: List[EventResults]


class SchemaGetPlaces(DefaultParam):
    results: List[GetPlacesResult] = None


class SchemaGetCollections(DefaultParam):
    results: List[GetCollectionsResult]


class SchemaGetMovieList(DefaultParam):
    results: List[GetMovieListResult]


class SchemaGetNews(DefaultParam):
    results: List[GetNewsResult]
