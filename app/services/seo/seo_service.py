import math
import asyncio
from typing import List, Dict
from .google_competetion import score_keyword_with_google


def heuristic_score_keyword(keyword: str, product_attributes: dict) -> float:
    score = 0.0
    buyer_terms = {"buy", "best", "price", "cheap", "online", "for", "new"}
    if any(term in keyword.lower() for term in buyer_terms):
        score += 0.35
    else:
        score += 0.15
    word_count = len(keyword.split())
    if 2 <= word_count <= 4:
        score += 0.35
    elif word_count > 4:
        score += 0.2
    else:
        score += 0.1
    if keyword.isalnum() or all(c.isalnum() or c in "- " for c in keyword):
        score += 0.2
    else:
        score += 0.05
    if product_attributes:
        key = keyword.lower()
        if any(str(v).lower() in key for v in product_attributes.values()):
            score += 0.1
    return min(1.0, score)

def rank_keywords(keywords: List[str], product_attributes: dict) -> List[dict]:
    ranked = [{"keyword": k, "heuristic_score": round(heuristic_score_keyword(k, product_attributes), 3)} for k in keywords]
    return sorted(ranked, key=lambda x: x["heuristic_score"], reverse=True)

async def score_keywords_with_google(keywords: List[str], product_attributes: dict, max_keywords: int = 10) -> List[dict]:
    keywords = keywords[:max_keywords]
    tasks = [score_keyword_with_google(k) for k in keywords]
    google_results = await asyncio.gather(*tasks, return_exceptions=True)
    combined = []
    for k, gres in zip(keywords, google_results):
        google_info = {"total": 0, "competition_score": 0.0, "difficulty": "unknown"}
        if isinstance(gres, dict):
            google_info = gres.get("google", google_info)
        heur = heuristic_score_keyword(k, product_attributes)
        combined_score = round(0.6*heur + 0.4*(1-google_info["competition_score"]), 3)
        combined.append({
            "keyword": k,
            "heuristic_score": round(heur, 3),
            "google_total_results": google_info["total"],
            "google_competition_score": google_info["competition_score"],
            "google_difficulty": google_info["difficulty"],
            "combined_score": combined_score
        })
    return sorted(combined, key=lambda x: x["combined_score"], reverse=True)
