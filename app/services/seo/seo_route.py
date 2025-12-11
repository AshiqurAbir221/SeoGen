# from fastapi import APIRouter, HTTPException
# from typing import List
# from .seo_service import rank_keywords, score_keywords_with_google
# from .seo_schema import SEORequest, SEOResponse, KeywordScore
# import asyncio

# router = APIRouter(prefix="/seo", tags=["SEO"])

# @router.post("/score-keywords", response_model=SEOResponse)
# async def score_keywords_endpoint(request: SEORequest):
#     if not request.keywords:
#         raise HTTPException(status_code=400, detail="No keywords provided")

#     # Step 1: heuristic ranking
#     ranked = rank_keywords(request.keywords, request.product_attributes)

#     # Step 2: augment with Google scoring
#     try:
#         google_results = await score_keywords_with_google(
#             [r["keyword"] for r in ranked],
#             request.product_attributes,
#             max_keywords=10
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Google scoring failed: {str(e)}")

#     return SEOResponse(results=google_results)
