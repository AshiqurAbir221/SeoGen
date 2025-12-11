# from pydantic import BaseModel
# from typing import List, Dict, Optional

# class Attributes(BaseModel):
#     category: Optional[str] = None
#     color: Optional[str] = None
#     material: Optional[str] = None
#     brand: Optional[str] = None
#     other: Optional[str] = None

# class ProductResult(BaseModel):
#     title: str
#     description: str
#     attributes: Attributes
#     seo_keywords: List[str]
#     seo_keywords_ranked: Optional[List[Dict]] = None
#     google_competition: Optional[List[Dict]] = None
#     db_saved: Optional[bool] = None



from pydantic import BaseModel
from typing import List, Optional, Dict


class Attributes(BaseModel):
    category: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    brand: Optional[str] = None
    other: Optional[str] = None


class PriceRange(BaseModel):
    min_price: float
    avg_price: float
    max_price: float


class ProductResult(BaseModel):
    title: str
    description: str
    short_description: str
    meta_title: str
    meta_description: str
    tags: List[str]
    promotional_tags: List[str]
    price_range: PriceRange
    db_saved: Optional[bool] = None
    db_error: Optional[str] = None
