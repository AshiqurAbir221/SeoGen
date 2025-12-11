from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    attributes = Column(JSON)
    keywords = relationship("Keyword", back_populates="product", cascade="all, delete-orphan")

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    keyword = Column(String)
    heuristic_score = Column(Float)
    google_total_results = Column(Integer)
    google_competition_score = Column(Float)
    google_difficulty = Column(String)
    combined_score = Column(Float)
    product = relationship("Product", back_populates="keywords")
