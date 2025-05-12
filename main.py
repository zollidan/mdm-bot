import asyncio
import datetime
import logging
import os
from aiogram import F, Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from pydantic_settings import BaseSettings, SettingsConfigDict
from art import tprint
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, PrimaryKeyConstraint, create_engine, select
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship

class Settins(BaseSettings):
    BOT_TOKEN: str
    
    model_config = SettingsConfigDict(env_file= os.path.join(os.path.dirname(__file__), ".env"))

settings = Settins()

logger = logging.getLogger(__name__)
dp = Dispatcher()
engine = create_engine("sqlite:///database.db", echo=True)

class Base(DeclarativeBase):
    created_date = Column(DateTime, default=datetime.datetime.now())

def create_tables():
    Base.metadata.create_all(engine)

class Favorite(Base):    
    __tablename__ = 'favorites'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'product_id'),
    )
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.telegram_id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    
    user: Mapped["User"] = relationship(back_populates="favorites")
    product: Mapped["Product"] = relationship(back_populates="favorites")

class Product(Base):
    __tablename__ = 'products'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String())
    vendor_code: Mapped[str] = mapped_column(String())
    price: Mapped[float] = mapped_column(Float())
    image: Mapped[str] = mapped_column(String())
    
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="product")
    orders: Mapped[list["Orders"]] = relationship(back_populates="product")
    
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
    
class Orders(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.telegram_id'))
    quantity: Mapped[int] = mapped_column(Integer)
    summ: Mapped[float] = mapped_column(Float)
    
    product: Mapped["Product"] = relationship(back_populates="orders")
    user: Mapped["User"] = relationship(back_populates="orders")

class Reviews(Base):
    __tablename__ = 'reviews'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.telegram_id'))
    user_text: Mapped[str] = mapped_column(String)
    
    user: Mapped["User"] = relationship(back_populates="reviews")


class SearchForm(StatesGroup):
    vendor_code_search = State()

def main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Поиск", callback_data="search")
    kb.button(text="Моя корзина", callback_data="cart")
    kb.button(text="Избранное", callback_data="favorites")
    kb.button(text="Профиль", callback_data="profile")
    kb.button(text="Заказы", callback_data="orders")
    kb.button(text="Оставить отзыв", callback_data="review")
    kb.button(text="Помощь", callback_data="help")

    kb.adjust(1)
    return kb.as_markup()

def productNotFoundKb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Искать еще раз", callback_data="search")
    kb.button(text="Главное меню", callback_data="main_page")
    
    kb.adjust(1)
    return kb.as_markup()

def productKb(product: int, is_fav: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if is_fav:
        kb.button(text="Удалить из избранного", callback_data=f"remove_fav_{product}")
    else:
        kb.button(text="Добавить в избранное", callback_data=f"add_fav_{product}")
    kb.button(text="Добавить в корзину", callback_data=f"add_cart_{product}")
    kb.button(text="Вопрос по товару для менеджера", callback_data=f"answ_{product}")
    kb.button(text="Назад", callback_data="main_page")

    kb.adjust(1)
    return kb.as_markup()

def editProfileKb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Изменить профиль", callback_data="change_profile")
    kb.button(text="Назад", callback_data="main_page")

    kb.adjust(1)
    return kb.as_markup()

def helpKb(user_telegram_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="Написать на почту", callback_data="help_send_email")
    kb.button(text="Позвонить", callback_data="help_call")
    kb.button(text="Написать в телеграм", callback_data="help_send_tg")
    kb.button(text="Назад", callback_data="main_page")

    kb.adjust(1)
    return kb.as_markup()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    
    with Session(engine) as session:
        logger.info(f"User {message.from_user.id} find in db")
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        user = session.scalar(stmt)
        if user is None:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                name=message.from_user.full_name,
                phone_number="",
                address=""
            )
            session.add(user)
            session.commit()
            session.refresh()
            logger.info(f"User {message.from_user.id} added to db")
            return await message.answer("Привет! Я бот, который поможет тебе найти нужный товар. Чтобы начать, выбери один из пунктов меню ниже.", reply_markup=main_kb())

    await message.answer(f"Hello {message.from_user.username}, Преветственное сообщение!", reply_markup=main_kb())

@dp.callback_query(F.data == "main_page")
async def main_page(callback: CallbackQuery):
    return callback.message.answer("Вы на главной страницу чтобы продолжить выберите действие!", reply_markup=main_kb())

@dp.callback_query(F.data == "search")
async def search_handler(callback: CallbackQuery, state: FSMContext) -> None:
    
    await state.set_state(SearchForm.vendor_code_search)
    
    await callback.message.answer("Введите артикул товара")
    
    await callback.answer("")
    
@dp.message(SearchForm.vendor_code_search)
async def process_vendor_code_search(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    vendor_code = message.text
    
    with Session(engine) as session:
        logger.info(f"User {user_id} search in db")
        try:
            stmt = select(Product).where(Product.vendor_code == vendor_code)
            product = session.scalars(stmt).first()
            
            if product is None:
                return await message.answer("Товары не найдены.", reply_markup=productNotFoundKb())
            
            fav_stmt = select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product.id
            )
            favorite = session.scalars(fav_stmt).first()
            is_favorite = favorite is not None
            
            return await message.answer_photo(
                photo=product.image,
                caption=f"Товар: {product.name}\nАртикул: {product.vendor_code}\nЦена: {product.price} руб.\n",
                reply_markup=productKb(product.id, is_fav=is_favorite)
            )
            
        except Exception as e:
            logger.error(f"Ошибка при поиске товара: {e}")
            return await message.answer("Ошибка при поиске товара!")
        
@dp.callback_query(F.data.startswith("add_fav_"))
async def add_product_to_favorites(callback: CallbackQuery):
    
    await callback.answer('')
    try:
        with Session(engine) as session:
            fav = Favorite(
                user_id=callback.from_user.id,
                product_id=str(callback.data).split("_")[2]
            )
            session.add(fav)
            session.commit()
            session.refresh()
        
        return callback.message.answer("Товар успешно добавлен!", reply_markup=main_kb())
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в избранное: {e}")
        return callback.message.answer("Ошибка при добавлении товара в избранное!")

@dp.callback_query(F.data == 'favorites')
async def favorites_list(callback: CallbackQuery):
    await callback.answer('')
    user_id: int = callback.from_user.id
    
    try:
        with Session(engine) as session:
            stmt = select(Product).join(Favorite, Favorite.product_id == Product.id).where(Favorite.user_id == user_id)
            products = session.scalars(stmt).all()
            
            if not products:
                await callback.message.answer("В списке избранного пусто(", reply_markup=main_kb())
                return
            
            message = "⭐ Ваши избранные товары:\n\n"
            for product in products:
                message += f"🔹 {product.name} - {product.price} руб.\n"
            
            await callback.message.answer(message)
            
    except Exception as e:
        logger.error(f"Ошибка при получении избранных товаров: {e}")
        await callback.message.answer("Ошибка при получении избранных товаров")

@dp.callback_query(F.data == 'profile')
async def profile_page(callback: CallbackQuery):
    logger.info(f"Parsing user {callback.from_user.id} profile page")
    try:
        with Session(engine) as session:
            stmt = select(User).where(User.telegram_id == callback.from_user.id)
            user = session.scalars(stmt).first()
    except:
        logger.error("Ошибка при получении пользователя")
        return callback.message.answer(f"Произошла ошибка при получении пользователя")
    return callback.message.answer(f"Ваш профиль:\n\n{user.name}\n{user.phone_number}\n{user.address}", reply_markup=editProfileKb())

@dp.callback_query(F.data == 'orders')
async def orders_list(callback: CallbackQuery):
    await callback.answer('')
    user_id: int = callback.from_user.id
    
    try:
        with Session(engine) as session:
            stmt = select(Orders).where(Orders.user_id == user_id)
            orders = session.scalars(stmt).all()
            
            if not orders:
                await callback.message.answer("В списке заказов пусто(", reply_markup=main_kb())
                return
            
            message = "Ваши заказы:\n\n"
            for order in orders:
                message += f"🔹 {order.id} - {order.summ} руб.\n"
            
            await callback.message.answer(message)
    except Exception as e:
        logger.error(f"Ошибка при получении избранных товаров: {e}")
        await callback.message.answer("Ошибка при получении избранных товаров")
@dp.callback_query(F.data == 'help')
async def help_page(callback: CallbackQuery):
    return callback.message.answer("Если возникли проблемы вы можете нам написать или позвонить и менеджер сразу вам перезвонит!\n Наши контакты:\nТелефон: 839819381", reply_markup=helpKb(callback.from_user.id))

async def main() -> None:
    create_tables()
    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(filename='mdm.log', level=logging.INFO)
    logger.info('Started')
    tprint("MDMBOT")
    asyncio.run(main())