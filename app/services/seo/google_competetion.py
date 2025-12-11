import os
import math
import asyncio
import httpx
from dotenv import load_dotenv
from cachetools import TTLCache, cached

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    pass  # calling code handles missing keys gracefully

_cache = TTLCache(maxsize=1024, ttl=300)  # 5 minutes TTL

@cached(_cache)
async def _fetch_google_count(keyword: str) -> int:
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        raise RuntimeError("Google API key or CSE ID not configured")

    endpoint = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": keyword, "num": 1}

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(endpoint, params=params)
        resp.raise_for_status()
        data = resp.json()

    total = data.get("searchInformation", {}).get("totalResults")
    try:
        return int(total) if total is not None else 0
    except Exception:
        return 0

def _map_count_to_competition(total_results: int) -> dict:
    if total_results <= 0:
        return {"total": 0, "competition_score": 0.0, "difficulty": "unknown"}

    logv = math.log10(total_results)
    norm = max(0.0, min(1.0, (logv - 1) / (9 - 1)))

    if total_results < 1_000:
        diff = "low"
    elif total_results < 100_000:
        diff = "medium"
    else:
        diff = "high"

    return {"total": total_results, "competition_score": round(norm, 3), "difficulty": diff}

async def score_keyword_with_google(keyword: str) -> dict:
    total = await _fetch_google_count(keyword)
    mapped = _map_count_to_competition(total)
    return {"keyword": keyword, "google": mapped}
