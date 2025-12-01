import datetime
from typing import List, Optional
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# MARK: models

class Base(DeclarativeBase):
    created_date = Column(DateTime, default=datetime.datetime.now)

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

    # Складские остатки
    stock_chashnikovo: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Москва, Чашниково
    stock_kantemirovskaya: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Москва, Кантемировская
    stock_spb: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Санкт-Петербург
    stock_voronezh: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Воронеж
    stock_korolev: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Королёв
    stock_krasnodar: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Краснодар
    stock_kazan: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Казань
    stock_online: Mapped[Optional[str]] = mapped_column(String(), nullable=True)  # Интернет-магазин

    # Цены для Беларуси
    price_byn_legal: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # Цена для ЮЛ (Бел. BYN)
    price_byn_retail: Mapped[Optional[float]] = mapped_column(Float(), nullable=True)  # Цена для ФЛ (Бел. BYN)

    favorites: Mapped[List["Favorite"]] = relationship(back_populates="product")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItems"]] = relationship(back_populates="product")
    
class Orders(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.telegram_id')) 
    total_sum: Mapped[float] = mapped_column(Float)  # общая сумма заказа
    status: Mapped[str] = mapped_column(String(50), default="processing")
    delivery_method: Mapped[str] = mapped_column(String(100), nullable=True)
    payment_method: Mapped[str] = mapped_column(String(100), nullable=True)
    tracking_number: Mapped[str] = mapped_column(String(100), nullable=True)
    order_date: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now)
    
    # Отношения
    user: Mapped["User"] = relationship(back_populates="orders")
    order_items: Mapped[List["OrderItems"]] = relationship(back_populates="order")

class OrderItems(Base):
    __tablename__ = 'order_items'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)  # цена товара на момент заказа
    
    # Отношения
    order: Mapped["Orders"] = relationship(back_populates="order_items")
    product: Mapped["Product"] = relationship(back_populates="order_items")

class User(Base):
    __tablename__ = 'users'
    
    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(), nullable=True)
    name: Mapped[str] = mapped_column(String())
    phone_number: Mapped[str] = mapped_column(String())
    address: Mapped[str] = mapped_column(String())
    
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")
    orders: Mapped[list["Orders"]] = relationship(back_populates="user")
    reviews: Mapped[list["Reviews"]] = relationship(back_populates="user")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="user")

class Reviews(Base):
    __tablename__ = 'reviews'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.telegram_id'))
    user_text: Mapped[str] = mapped_column(String)
    
    user: Mapped["User"] = relationship(back_populates="reviews")
