from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=1, max_length=1000)
    source: str = Field(min_length=1, max_length=50)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    source: str
    created_at: datetime


class PriceHistoryCreate(BaseModel):
    price: float = Field(gt=0)


class PriceHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    price: float
    currency: str
    scraped_at: datetime

class PriceStats(BaseModel):
    product_id : int
    records : int 
    min_price : float
    max_price: float 
    avg_price: float 
    latest_price: float 
    change_30d_pct: float |  None 