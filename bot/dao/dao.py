from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
from sqlalchemy import delete, select
from bot.dao.base import BaseDAO
from bot.dao.models import User, Product, Favorite

class ProductDao(BaseDAO[Product]):
    model = Product
    
    @classmethod
    async def find_one_or_none_by_name(cls, product_name: str, session: AsyncSession):
        # Найти запись по ID
        logger.info(f"Поиск {cls.model.__name__} с vendor_code: {product_name}")
        try:
            query = select(cls.model).filter_by(name=product_name)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Запись с ID {product_name} найдена.")
            else:
                logger.info(f"Запись с ID {product_name} не найдена.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске записи с ID {product_name}: {e}")
            raise
        
    @classmethod
    async def find_one_or_none_by_vendor_code(cls, product_vendor_code: str, session: AsyncSession):
        # Найти запись по vendor_code
        logger.info(f"Поиск {cls.model.__name__} с vendor_code: {product_vendor_code}")
        try:
            query = select(cls.model).filter_by(vendor_code=product_vendor_code)  # заменить name на vendor_code при необходимости
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            if record:
                logger.info(f"Товар с vendor_code {product_vendor_code} найден.")
            else:
                logger.info(f"Товар с vendor_code {product_vendor_code} не найден.")
            return record
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске товара с vendor_code {product_vendor_code}: {e}")
            raise

        


class UserDAO(BaseDAO[User]):
    model = User




class FavoriteDAO(BaseDAO[Favorite]):
    model = Favorite

    @classmethod
    async def get_user_favorites(cls, user_id: int, session: AsyncSession):
        try:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении избранных товаров пользователя {user_id}: {e}")
            raise

    @classmethod
    async def add_favorite(cls, user_id: int, product_id: int, session: AsyncSession):
        logger.info(f"Добавление избранного: user_id={user_id}, product_id={product_id}")
        try:
            favorite = Favorite(user_id=user_id, product_id=product_id)
            session.add(favorite)
            await session.flush()
            return favorite
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при добавлении избранного: {e}")
            raise

    @classmethod
    async def remove_favorite(cls, user_id: int, product_id: int, session: AsyncSession):
        logger.info(f"Удаление избранного: user_id={user_id}, product_id={product_id}")
        try:
            stmt = delete(cls.model).filter_by(user_id=user_id, product_id=product_id)
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Ошибка при удалении избранного: {e}")
            raise
