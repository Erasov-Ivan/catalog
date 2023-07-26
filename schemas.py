from pydantic import BaseModel
from typing import Union, Any



class BaseResponse(BaseModel):
    error: bool
    message: str
    payload: Union[Any, None] = None


class Catalog(BaseModel):
    id: int
    name: str


class CatalogList(BaseModel):
    totalcount: int
    catalogs: list[Catalog]


class CatalogListResponse(BaseResponse):
    payload: CatalogList


class Item(BaseModel):
    id: int
    name: str
    description: str
    price: int
    picture_url: str


class ItemList(BaseModel):
    totalcount: int
    items: list[Item]


class ItemListResponse(BaseResponse):
    payload: ItemList