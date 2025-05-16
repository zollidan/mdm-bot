import datetime
from typing import List, Optional
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, PrimaryKeyConstraint, create_engine, select
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship

# MARK: models

class Base(DeclarativeBase):
    created_date = Column(DateTime, default=datetime.datetime.now())

class Favorite(Base):    
    __tablename__ = 'favorites'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'product_id'),
    )
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    
    user: Mapped["User"] = relationship(back_populates="favorites")
    product: Mapped["Product"] = relationship(back_populates="favorites")
    
class CartItem(Base):
    __tablename__ = 'cart_items'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.telegram_id'))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    added_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    
    user: Mapped["User"] = relationship(back_populates="cart_items")
    product: Mapped["Product"] = relationship(back_populates="cart_items")
    

class Product(Base):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String())  # URL товара
    name: Mapped[str] = mapped_column(String())  # Название товара
    vendor_code: Mapped[str] = mapped_column(String())  # Код поставщика
    price: Mapped[float] = mapped_column(Float())  # Цена в рублях
    currency_id: Mapped[str] = mapped_column(String())  # Валюта (например, "RUR")
    category_id: Mapped[int] = mapped_column(Integer)  # ID категории
    model: Mapped[str] = mapped_column(String())  # Модель товара
    vendor: Mapped[str] = mapped_column(String())  # Производитель
    description: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Описание товара
    manufacturer_warranty: Mapped[bool] = mapped_column(Boolean())  # Гарантия производителя
    image: Mapped[str] = mapped_column(String())  # URL изображения (первое из списка Pictures)
    opt_price: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # Оптовая цена (Цена ОПТ, RUR)
    is_bestseller: Mapped[bool] = mapped_column(Boolean())  # Хит продаж (True/False)
    unit: Mapped[str] = mapped_column(String())  # Единица измерения (шт, кг и т.д.)
    usd_price: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # Цена в у.е. (Цена у.е.)
    availability: Mapped[str] = mapped_column(String())  # Наличие (есть/нет)
    status: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Статус товара
    
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="product")
    orders: Mapped[List["Orders"]] = relationship(back_populates="product")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product")
    
class User(Base):
    __tablename__ = 'users'
    
    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String())
    address: Mapped[str] = mapped_column(String())
    
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")
    orders: Mapped[list["Orders"]] = relationship(back_populates="user")
    reviews: Mapped[list["Reviews"]] = relationship(back_populates="user")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="user")
    
class Orders(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.telegram_id')) 
    quantity: Mapped[int] = mapped_column(Integer) # количество товара
    summ: Mapped[float] = mapped_column(Float) # сумма заказа
    status: Mapped[str] = mapped_column(String(50), default="processing")  # статус заказа
    delivery_method: Mapped[str] = mapped_column(String(100), nullable=True)  # метод доставки
    payment_method: Mapped[str] = mapped_column(String(100), nullable=True)  # метод оплаты
    tracking_number: Mapped[str] = mapped_column(String(100), nullable=True)  # трекинг-номер
    
    product: Mapped["Product"] = relationship(back_populates="orders")
    user: Mapped["User"] = relationship(back_populates="orders")

class Reviews(Base):
    __tablename__ = 'reviews'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.telegram_id'))
    user_text: Mapped[str] = mapped_column(String)
    
    user: Mapped["User"] = relationship(back_populates="reviews")
