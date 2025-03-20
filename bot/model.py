from sqlalchemy import BigInteger, Text, Integer, Boolean, Float
from bot.database import Base
from sqlalchemy.orm import mapped_column, Mapped
    
class User(Base):
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(Text)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"

class Product(Base):
    __tablename__ = "products"

    offer_id: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(Text)
    currencyId: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(Text)
    vendor: Mapped[str] = mapped_column(Text)
    vendorCode: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    manufacturer_warranty: Mapped[bool] = mapped_column(Boolean)
    pictures: Mapped[str] = mapped_column(Text)
    price_wholesale_rub: Mapped[float] = mapped_column(Float)
    bestseller: Mapped[int] = mapped_column(Integer)
    unit: Mapped[str] = mapped_column(Text)
    price_u_e: Mapped[float] = mapped_column(Float)
    quantity_in_stock_moscow_chashnikovo: Mapped[str] = mapped_column(Text)
    quantity_in_stock_moscow_kantemirovskaya: Mapped[str] = mapped_column(Text)
    quantity_in_stock_saint_petersburg: Mapped[str] = mapped_column(Text)
    quantity_in_stock_voronezh: Mapped[str] = mapped_column(Text)
    price_for_company_byn: Mapped[float] = mapped_column(Float)
    price_for_individual_byn: Mapped[float] = mapped_column(Float)
    in_stock: Mapped[bool] = mapped_column(Boolean)
    product_status: Mapped[str] = mapped_column(Text)