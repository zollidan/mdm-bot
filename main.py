import asyncio
import datetime
import logging
from aiogram import F, Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from pydantic_settings import BaseSettings
from art import tprint
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, PrimaryKeyConstraint, create_engine, select
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship
class Settins(BaseSettings):
    BOT_TOKEN: str

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
    
class User(Base):
    __tablename__ = 'users'
    
    telegram_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String())
    address: Mapped[str] = mapped_column(String())
    
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")
    
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

def productKb(product: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Добавить в избранное", callback_data=f"add_fav_{product}")
    kb.button(text="Добавить в корзину", callback_data=f"add_cart_{product}")
    kb.button(text="Вопрос по товару для менеджера", callback_data=f"answ_{product}")
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

@dp.callback_query(F.data == "search")
async def search_handler(callback: CallbackQuery, state: FSMContext) -> None:
    
    await state.set_state(SearchForm.vendor_code_search)
    
    await callback.message.answer("Введите артикул товара")
    
    await callback.answer("")
    
@dp.message(SearchForm.vendor_code_search)
async def process_vendor_code_search(message: Message, state: FSMContext) -> None:
    
    with Session(engine) as session:
        logger.info(f"User {message.from_user.id} search in db")
        try:
            stmt = select(Product).where(Product.id == int(message.text))
            product = session.scalars(stmt).first()
        except:
            return await message.answer("Ошибка при поиске товара!")
        if product is None:
            return await message.answer("Товары не найдены.", reply_markup=productNotFoundKb())
        
        return await message.answer(
            f"Товар: {product.name}\n"
            f"Артикул: {product.vendor_code}\n"
            f"Цена: {product.price} руб.\n"
            f"Изображение: {product.image}",
            reply_markup=productKb(product.id)
        )
        
@dp.callback_query(F.data.startswith("add_fav_"))
async def add_product_to_favarites(callback: CallbackQuery):
    
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
    except:
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

async def main() -> None:
    create_tables()
    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(filename='mdm.log', level=logging.INFO)
    logger.info('Started')
    tprint("MDMBOT")
    asyncio.run(main())