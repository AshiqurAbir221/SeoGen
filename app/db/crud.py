from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Product, Keyword

async def save_product_result(db: AsyncSession, title: str, description: str, attributes: dict, keywords: list):
    product = Product(title=title, description=description, attributes=attributes)
    db.add(product)
    await db.flush()  # Get ID

    for k in keywords:
        keyword = Keyword(
            product_id=product.id,
            keyword=k["keyword"],
            heuristic_score=k.get("heuristic_score"),
            google_total_results=k.get("google_total_results", 0),
            google_competition_score=k.get("google_competition_score", 0.0),
            google_difficulty=k.get("google_difficulty", "unknown"),
            combined_score=k.get("combined_score", 0.0)
        )
        db.add(keyword)

    await db.commit()
    await db.refresh(product)
    return product.id

async def get_all_products(db: AsyncSession):
    result = await db.execute(select(Product))
    return result.scalars().all()
