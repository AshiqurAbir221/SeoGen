import httpx
import re
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


async def fetch_price_from_web(product_title: str, category: str = "") -> Dict:
    """
    Fetch real market prices using Google Custom Search API
    
    Args:
        product_title: The product name/title
        category: Optional product category for better search
    
    Returns:
        Dict with min_price, avg_price, max_price, source, samples_found
    """
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("⚠️ Google API credentials not configured")
        return {
            "min_price": None,
            "avg_price": None,
            "max_price": None,
            "source": "api_not_configured"
        }
    
    try:
        # Build search query focused on shopping/pricing
        query = f"{product_title} price buy"
        if category:
            query = f"{category} {query}"
        
        endpoint = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": 10  # Get top 10 results for better price sampling
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()
        
        # Extract prices from search results
        prices = []
        items = data.get("items", [])
        
        for item in items:
            # Combine title and snippet for price extraction
            text = f"{item.get('title', '')} {item.get('snippet', '')}"
            
            # Multiple regex patterns to catch different price formats
            price_patterns = [
                r'\$\s*(\d{1,5}(?:[.,]\d{2})?)',  # $299 or $299.99
                r'USD\s*(\d{1,5}(?:[.,]\d{2})?)',  # USD 299
                r'(\d{1,5}(?:[.,]\d{2})?)\s*(?:USD|dollars)',  # 299 USD
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        price = float(match.replace(',', ''))
                        # Filter out unrealistic prices (between $1 and $100,000)
                        if 1 < price < 100000:
                            prices.append(price)
                    except ValueError:
                        continue
        
        # Remove duplicates and sort
        prices = sorted(list(set(prices)))
        
        if not prices:
            print(f"⚠️ No prices found for: {product_title}")
            return {
                "min_price": None,
                "avg_price": None,
                "max_price": None,
                "source": "no_prices_found"
            }
        
        # Calculate statistics
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        print(f"✅ Found {len(prices)} prices for '{product_title}': ${min_price} - ${max_price}")
        
        return {
            "min_price": round(min_price, 2),
            "avg_price": round(avg_price, 2),
            "max_price": round(max_price, 2),
            "source": "google_search",
            "samples_found": len(prices)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            print("❌ Google API quota exceeded")
            return {
                "min_price": None,
                "avg_price": None,
                "max_price": None,
                "source": "api_quota_exceeded"
            }
        else:
            print(f"❌ HTTP error: {e}")
            return {
                "min_price": None,
                "avg_price": None,
                "max_price": None,
                "source": "api_error"
            }
    
    except Exception as e:
        print(f"❌ Price fetch error: {e}")
        return {
            "min_price": None,
            "avg_price": None,
            "max_price": None,
            "source": "error"
        }