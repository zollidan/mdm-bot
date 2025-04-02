

from bot.dao.base import BaseDAO
from bot.dao.models import User, Product

class ProductDao(BaseDAO[Product]):
    model = Product


class UserDAO(BaseDAO[User]):
    model = User

