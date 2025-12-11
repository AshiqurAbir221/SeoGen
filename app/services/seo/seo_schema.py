# from pydantic import BaseModel
# from typing import List, Optional

# class KeywordScore(BaseModel):
#     keyword: str
#     heuristic_score: float
#     google_total_results: int
#     google_competition_score: float
#     google_difficulty: str
#     combined_score: float

# class SEORequest(BaseModel):
#     keywords: List[str]
#     product_attributes: Optional[dict] = {}

# class SEOResponse(BaseModel):
#     results: List[KeywordScore]
