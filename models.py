from typing import Optional
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    offer_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    vendor: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    vendor_code: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    manufacturer_warranty: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pictures: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    wholesale_price_rur: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_bestseller: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    unit_of_measurement: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price_conventional_units: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stock_moscow_chashnikovo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stock_moscow_kantemirovskaya: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stock_saint_petersburg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stock_voronezh: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_legal_byn: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_individual_byn: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stock_korolev: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stock_krasnodar: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stock_kazan: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stock_klin: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    availability: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
