from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Any, Dict, List, cast
from app.services.product_analyzer.analyzer import analyze_product_image
from app.services.seo.seo_service import score_keywords_with_google
from app.services.pricing.price_fetcher import fetch_price_from_web  # NEW IMPORT
from app.db.database import get_db
from app.db.crud import save_product_result
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analyze", tags=["Product Analyzer"])
MAX_GOOGLE_KEYWORDS = 15

@router.post("/product")
async def analyze_product_endpoint(
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # Step 1: AI analyzes image
    result = analyze_product_image(image_bytes)
    if not isinstance(result, dict):
        return {"error": "Invalid response from image analyzer"}
    if "error" in result:
        return result

    attributes = result.get("attributes", {})
    product_title = result.get("title", "")
    category = attributes.get("category", "")
    
    # Step 2: Extract and rank keywords
    raw_keywords = result.get("seo_keywords", [])
    if not isinstance(raw_keywords, list):
        raw_keywords = [raw_keywords]
    keywords = [str(k) for k in raw_keywords if k]

    try:
        all_ranked = await score_keywords_with_google(
            keywords,
            attributes,
            max_keywords=MAX_GOOGLE_KEYWORDS
        )
    except Exception as e:
        print(f"Ranking failed: {e}")
        all_ranked = [{"keyword": k, "combined_score": 0.5} for k in keywords[:6]]

    sorted_tags = sorted(all_ranked, key=lambda x: x["combined_score"], reverse=True)
    top_6_tags = [tag["keyword"] for tag in sorted_tags[:6]]

    # Step 3: Fetch REAL prices from web 🔥
    print(f"🔍 Fetching prices for: {product_title}")
    price_range = await fetch_price_from_web(product_title, category)
    
    # If web search found no prices, return None instead of AI estimate
    if price_range.get("min_price") is None:
        print(f"⚠️ Could not find web prices, source: {price_range.get('source')}")
        price_range = None  # Don't return unreliable data
    else:
        print(f"✅ Web prices found: ${price_range['min_price']} - ${price_range['max_price']}")

    # Get promotional tags
    promotional_tags = result.get("promotional_tags", [])[:6]

    # Save to DB
    saved = False
    error_msg = None
    try:
        await save_product_result(
            db=db,
            title=product_title,
            description=result.get("description", ""),
            attributes=attributes,
            keywords=all_ranked
        )
        saved = True
    except Exception as e:
        error_msg = str(e)
        print(f"Database save failed: {e}")

    # Return clean output
    final_output = {
        "title": product_title,
        "description": result.get("description"),
        "short_description": result.get("short_description"),
        "meta_title": result.get("meta_title"),
        "meta_description": result.get("meta_description"),
        "tags": top_6_tags,
        "promotional_tags": promotional_tags,
        "db_saved": saved
    }
    
    # Only include price_range if web search was successful
    if price_range:
        final_output["price_range"] = price_range

    if not saved:
        final_output["db_error"] = error_msg

    return final_output