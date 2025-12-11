from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def analyze_product_image(image_bytes: bytes):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            """
You are an expert e-commerce copywriter specializing in product listings that convert browsers into buyers.

Analyze this product image and create compelling, sales-focused content for an online store. Write as if you're selling to excited customers, not just describing what you see.

Return ONLY valid JSON with these fields:

- "title": A compelling, click-worthy product title (50-70 characters) that includes the product type and key appeal factor
- "description": (120–140 words MAX, strictly follow) A persuasive product description that:
  * Opens with an exciting, emotional hook about the product's appeal or benefit
  * Highlights key features and what makes this special
  * Emphasizes emotional benefits and who this is perfect for
  * Uses vivid, engaging language that creates desire
  * Avoids generic phrases like "this product" or robotic descriptions
- "short_description": A punchy 1-2 sentence teaser (150-160 characters) perfect for search results and previews
- "meta_title": SEO-optimized title (50-60 characters) with primary keyword and appeal
- "meta_description": SEO-friendly description (150-160 characters) that encourages clicks
- "seo_keywords": Array of 10-15 highly relevant SEO keywords and phrases (e.g., ["running shoes", "men's athletic footwear", "breathable sneakers"])
- "promotional_tags": Array of 5-6 compelling promotional phrases (e.g., ["Limited Edition", "Premium Quality", "Best Seller"])
- "attributes": Product attributes as {"category": "...", "color": "...", "material": "...", "brand": "...", "other": "..."}

Write in an engaging, professional tone that builds excitement and urgency. Focus on benefits over features. Make customers want to click "Add to Cart."

Return ONLY the JSON object. No markdown code blocks, no explanations, no preamble. Just pure JSON starting with { and ending with }.
"""
        ]
    )

    text_response = response.text
    if not isinstance(text_response, str) or not text_response:
        return {"error": "Empty or non-string response", "raw_response": text_response}
    
    # Clean up response - remove markdown code blocks if present
    cleaned = text_response.strip()
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if json_match:
        candidate = json_match.group(1)
    else:
        # If no code blocks, try to extract JSON directly
        json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        candidate = json_match.group(1) if json_match else cleaned
    
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        return {"error": "JSON parsing failed", "raw_response": text_response, "exception": str(e)}