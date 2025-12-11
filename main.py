from fastapi import FastAPI
from app.services.product_analyzer.analyzer_route import router as analyzer_router
# from app.services.seo.seo_route import router as seo_router



app = FastAPI(title="E-commerce AI Product Analyzer")

# Include routers
app.include_router(analyzer_router)
# app.include_router(seo_router)