from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Boolean, Float, Integer, String, Text, ForeignKey
from bot.dao.database import Base


from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, BigInteger
from bot.dao.database import Base

# Если необходимо, добавьте связи favorites к существующим моделям User и Product


class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"


class Product(Base):
    __tablename__ = 'products'

    offer_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10))
    category_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    vendor: Mapped[str] = mapped_column(String)
    vendor_code: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    warranty: Mapped[bool] = mapped_column(Boolean, default=False)
    pictures: Mapped[str] = mapped_column(Text)  # возможно, это список ссылок в виде строки
    wholesale_price: Mapped[float] = mapped_column(Float)
    bestseller: Mapped[bool] = mapped_column(Boolean, default=False)
    unit: Mapped[str] = mapped_column(String(10))
    price_ue: Mapped[float] = mapped_column(Float)
    stock_moscow_chashnikovo: Mapped[str] = mapped_column(String)  # строка типа "более 100"
    stock_moscow_kantemirovskaya: Mapped[int] = mapped_column(Integer)
    stock_spb: Mapped[int] = mapped_column(Integer)
    stock_voronezh: Mapped[int] = mapped_column(Integer)
    price_legal_by: Mapped[float] = mapped_column(Float)
    price_individual_by: Mapped[float] = mapped_column(Float)
    availability: Mapped[str] = mapped_column(String(20))  # например, "есть"
    product_status: Mapped[str] = mapped_column(String(50))

class Favorite(Base):
    __tablename__ = 'favorites'
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="unique_favorite"),)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))

    user: Mapped["User"] = relationship("User", backref="favorites")
    product: Mapped["Product"] = relationship("Product", backref="favorited_by")
