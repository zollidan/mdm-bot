"""
Core modules: database, models, config, search
"""

from .config import settings
from .database import AsyncSessionFactory, create_tables
from .models import User, Product, CartItem, Favorite, Orders, OrderItems, Reviews
from .search import MeiliSearchClient, get_meili_client

__all__ = [
    "settings",
    "AsyncSessionFactory",
    "create_tables",
    "User",
    "Product",
    "CartItem",
    "Favorite",
    "Orders",
    "OrderItems",
    "Reviews",
    "MeiliSearchClient",
    "get_meili_client",
]
