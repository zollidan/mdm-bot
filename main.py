import asyncio
import datetime
import logging
import os
from typing import List, Optional
from aiogram import F, Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from pydantic_settings import BaseSettings, SettingsConfigDict
from art import tprint
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, PrimaryKeyConstraint, create_engine, select
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship

# MARK: settings

class Settins(BaseSettings):
    BOT_TOKEN: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    
    model_config = SettingsConfigDict(env_file= os.path.join(os.path.dirname(__file__), ".env"))

settings = Settins()

# MARK: db

logger = logging.getLogger(__name__)
dp = Dispatcher()
url = f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(url, echo=True)

class Base(DeclarativeBase):
    created_date = Column(DateTime, default=datetime.datetime.now())

def create_tables():
    Base.metadata.create_all(engine)

# MARK: models

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

# MARK: states

# Класс состояний для формы поиска
class SearchForm(StatesGroup):
    vendor_code_search = State()
    name_search = State()
    
# Класс состояний для формы профиля
class ProfileForm(StatesGroup):
    name = State()
    phone = State()
    address = State()

# MARK: kbs

def main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Поиск", callback_data="search")
    kb.button(text="Моя корзина", callback_data="cart")
    kb.button(text="Избранное", callback_data="favorites")
    kb.button(text="Профиль", callback_data="profile")
    kb.button(text="Заказы", callback_data="orders")
    # kb.button(text="Оставить отзыв", callback_data="review")
    kb.button(text="Помощь", callback_data="help")

    kb.adjust(1)
    return kb.as_markup()

def search_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 По названию", callback_data="search_by_name")
    kb.button(text="🔙 Назад", callback_data="main_page")
    kb.adjust(2, 2)
    return kb.as_markup()

def product_not_found_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔢 Поиск по артикулу", callback_data="search_by_code")
    kb.button(text="📝 Поиск по названию", callback_data="search_by_name")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    
    kb.adjust(2, 2)
    return kb.as_markup()

def product_kb(product_id: int, is_fav: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для страницы товара.
    
    Args:
        product_id: ID товара
        is_fav: Находится ли товар в избранном
    
    Returns:
        Клавиатура для товара
    """
    kb = InlineKeyboardBuilder()
    
    # Кнопка добавления в корзину
    kb.button(
        text="🛒 Добавить в корзину", 
        callback_data=f"add_cart_{product_id}"
    )
    
    # Динамическая кнопка избранного в зависимости от статуса
    if is_fav:
        kb.button(
            text="❌ Удалить из избранного", 
            callback_data=f"remove_fav_{product_id}"
        )
    else:
        kb.button(
            text="⭐ Добавить в избранное", 
            callback_data=f"add_fav_{product_id}"
        )
    
    # Дополнительные действия с товаром
    kb.button(
        text="📋 Характеристики", 
        callback_data=f"specs_{product_id}"
    )
    kb.button(
        text="💬 Отзывы", 
        callback_data=f"reviews_{product_id}"
    )
    
    # Навигационные кнопки
    kb.button(text="🔍 К поиску", callback_data="search")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    
    # Настраиваем расположение кнопок (2 кнопки в ряд)
    kb.adjust(1, 1, 2, 2, 2)
    
    return kb.as_markup()

def favorite_kb(results) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    # Добавляем товары в сообщение и кнопки для каждого товара
    for i, (product, favorite) in enumerate(results, 1):
        # Добавляем информацию о товаре в сообщение
        message += (
            f"<b>{i}. {product.name}</b>\n"
            f"📊 Артикул: {product.vendor_code}\n"
            f"💰 Цена: {product.price} руб.\n"
            f"📅 Добавлен: {favorite.created_date.strftime('%d.%m.%Y')}\n\n"
        )
        
        # Кнопки для каждого товара
        kb.button(text=f"📋 Карточка #{i}", callback_data=f"view_product_{product.id}")
        kb.button(text=f"🛒 В корзину #{i}", callback_data=f"add_cart_{product.id}")
        kb.button(text=f"❌ Удалить #{i}", callback_data=f"remove_fav_{product.id}")
    
    # Добавляем кнопки управления внизу
    kb.button(text="🔄 Обновить список", callback_data="favorites")
    kb.button(text="🛒 В корзину все", callback_data="add_all_to_cart")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    
    # Настраиваем расположение кнопок (3 кнопки для каждого товара в ряд, затем 3 кнопки управления)
    kb.adjust(3)
    return kb.as_markup()

def orders_kb(orders_by_date) -> InlineKeyboardMarkup:
    # Создаем клавиатуру для управления заказами
    kb = InlineKeyboardBuilder()
    
    # Добавляем заказы, сгруппированные по датам
    for date, date_orders in sorted(orders_by_date.items(), reverse=True):
        message += f"📅 <b>{date}</b>\n"
        
        for i, (order, product) in enumerate(date_orders, 1):
            message += (
                f"{i}. <b>{product.name}</b>\n"
                f"   📊 Артикул: {product.vendor_code}\n"
                f"   🔢 Количество: {order.quantity} шт.\n"
                f"   💰 Сумма: {order.summ:.2f} руб.\n"
            )
            
            # Добавляем кнопку для деталей заказа
            kb.button(
                text=f"📋 Заказ #{order.id}", 
                callback_data=f"order_details_{order.id}"
            )
    
    # Добавляем кнопки управления
    kb.button(text="📱 Связаться с менеджером", callback_data="contact_manager")
    kb.button(text="🔄 Обновить", callback_data="orders")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    
    # Настраиваем расположение кнопок
    kb.adjust(1)
    return kb.as_markup()

def profile_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Изменить имя", callback_data="edit_name")
    kb.button(text="📞 Изменить телефон", callback_data="edit_phone")
    kb.button(text="🏠 Изменить адрес", callback_data="edit_address")
    kb.button(text="📊 История заказов", callback_data="orders_history")
    kb.button(text="🔙 Назад", callback_data="main_page")
    kb.adjust(2, 2, 1)
    return kb.as_markup()

def help_kb(user_telegram_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="📞 Позвонить нам", callback_data="help_call")
    kb.button(text="✉️ Написать на почту", callback_data="help_send_email")
    kb.button(text="💬 Чат с поддержкой", callback_data="help_send_tg")
    kb.button(text="❓ Частые вопросы", callback_data="help_faq")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    
    kb.adjust(1)
    return kb.as_markup()


# MARK: /start

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    
    welcome_message = (
        "🎉 Добро пожаловать в MDM Bot! 🎉\n\n"
        "Мы рады приветствовать вас в нашем каталоге товаров!\n\n"
        "Здесь вы сможете:\n"
        "🔍 Искать товары по артикулу\n"
        "🛒 Добавлять товары в корзину\n"
        "⭐️ Сохранять понравившиеся товары в избранное\n"
        "📦 Оформлять заказы и отслеживать их статус\n\n"
        "Для начала работы выберите одно из действий на клавиатуре ниже 👇"
    )
    

    
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
            logger.info(f"User {message.from_user.id} added to db")
            return await message.answer(welcome_message, reply_markup=main_kb())
        
        cart_count = session.query(CartItem).filter(CartItem.user_id == message.from_user.id).count()
        favorites_count = session.query(Favorite).filter(Favorite.user_id == message.from_user.id).count()
        orders_count = session.query(Orders).filter(Orders.user_id == message.from_user.id).count()
        
        welcome_back_message = (
                f"👋 С возвращением в MDM Bot!\n\n"
                f"Рады снова видеть вас, {user.name}!\n\n"
                f"📊 Статистика вашего аккаунта:\n"
                f"🔸 Товаров в корзине: {cart_count}\n"
                f"⭐️ В избранном: {favorites_count}\n"
                f"📦 Активных заказов: {orders_count}\n\n"
                f"Чем могу помочь вам сегодня? Выберите действие на клавиатуре ниже 👇"
        )

        return await message.answer(welcome_back_message, reply_markup=main_kb())

# MARK: main_page

@dp.callback_query(F.data == "main_page")
async def main_page(callback: CallbackQuery):
    await callback.answer("")

    try:
        with Session(engine) as session:
            user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
            cart_count = session.query(CartItem).filter(CartItem.user_id == callback.from_user.id).count()
            favorites_count = session.query(Favorite).filter(Favorite.user_id == callback.from_user.id).count()
            orders_count = session.query(Orders).filter(Orders.user_id == callback.from_user.id).count()
    
            # Персонализированное приветствие
            greeting = f"👋 Здравствуйте, {user.name}!" if user else "👋 Здравствуйте!"
            
            main_page_text = (
                f"{greeting}\n\n"
                f"🛍 <b>MDM Store - ваш надежный поставщик</b>\n\n"
                f"📊 <b>Ваша статистика:</b>\n"
                f"🛒 Товаров в корзине: {cart_count}\n"
                f"⭐ Избранных товаров: {favorites_count}\n"
                f"📦 Активных заказов: {orders_count}\n\n"
                f"📣 <b>Специальные предложения:</b>\n"
                f"• Скидка 10% на все товары до 30 мая\n"
                f"• Бесплатная доставка при заказе от 5000 руб.\n\n"
                f"Выберите действие на клавиатуре ниже 👇"
            )
            
            return await callback.message.edit_text(
                main_page_text, 
                reply_markup=main_kb(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке главной страницы: {e}")
        return await callback.message.edit_text(
            "Добро пожаловать в MDM Store!\n\nВыберите действие на клавиатуре ниже 👇", 
            reply_markup=main_kb()
        )

# MARK: search

@dp.callback_query(F.data == "search")
async def search_handler(callback: CallbackQuery, state: FSMContext) -> None:
    # Обновляем интерфейс поиска
    search_message = (
        "🔍 <b>Поиск товаров</b>\n\n"
        "Выберите способ поиска товаров:\n"
        "• По названию товара\n"
        "Или введите артикул товара прямо сейчас:"
    )

    await callback.message.answer(
        search_message,
        reply_markup=search_kb(),
        parse_mode="HTML"
    )
    
    # Устанавливаем состояние для поиска по артикулу
    await state.set_state(SearchForm.vendor_code_search)
    await callback.answer("")
        

# Обработчик для поиска по названию
@dp.callback_query(F.data == "search_by_name")
async def search_by_name_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SearchForm.name_search)
    
    await callback.message.answer(
        "📝 <b>Поиск по названию</b>\n\n"
        "Введите название или часть названия товара:",
        parse_mode="HTML"
    )
    
    await callback.answer("")
        
# Обработчик для поиска по артикулу
@dp.message(SearchForm.vendor_code_search)
async def process_vendor_code_search(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    vendor_code = message.text
    
    await state.clear()  # Очищаем состояние после получения данных
    
    with Session(engine) as session:
        logger.info(f"User {user_id} search by vendor code: {vendor_code}")
        try:
            stmt = select(Product).where(Product.vendor_code == vendor_code)
            product = session.scalars(stmt).first()
            
            if product is None:
                # Улучшенное сообщение об отсутствии товара
                return await message.answer(
                    "🔍 <b>Товар не найден</b>\n\n"
                    f"К сожалению, товар с артикулом <code>{vendor_code}</code> не найден в нашей базе данных.\n\n"
                    "• Проверьте правильность ввода артикула\n"
                    "• Попробуйте поиск по названию товара\n",
                    parse_mode="HTML",
                    reply_markup=product_not_found_kb()
                )
            
            # Проверяем, добавлен ли товар в избранное
            fav_stmt = select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product.id
            )
            favorite = session.scalars(fav_stmt).first()
            is_favorite = favorite is not None
            
            # Формируем подробное описание товара
            product_info = (
                f"<b>{product.name}</b>\n\n"
                f"📋 <b>Информация о товаре:</b>\n"
                f"📊 Артикул: {product.vendor_code}\n"
                f"💰 Цена: {product.price} руб.\n"
                f"🏭 Производитель: {product.vendor}\n"
                f"📦 Наличие: {product.availability}\n\n"
            )
            
            if product.description:
                product_info += f"📝 <b>Описание:</b>\n{product.description[:300]}{'...' if len(product.description) > 300 else ''}\n\n"
            
            product_info += f"⚙️ Модель: {product.model}\n"
            
            if product.is_bestseller:
                product_info += "🔥 <b>ХИТ ПРОДАЖ!</b>\n\n"
            
            # Отправляем фото с описанием товара
            return await message.answer_photo(
                photo=product.image,
                caption=product_info,
                reply_markup=product_kb(product.id, is_fav=is_favorite),
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при поиске товара: {e}")
            return await message.answer(
                "😔 Произошла ошибка при поиске товара. Пожалуйста, попробуйте снова позже.",
                reply_markup=main_kb()
            )

# Обработчик для поиска по названию
@dp.message(SearchForm.name_search)
async def process_name_search(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    search_term = message.text
    
    await state.clear()  # Очищаем состояние после получения данных
    
    with Session(engine) as session:
        logger.info(f"User {user_id} search by name: {search_term}")
        try:
            # Поиск по частичному совпадению с названием
            stmt = select(Product).where(Product.name.ilike(f"%{search_term}%")).limit(5)
            products = session.scalars(stmt).all()
            
            if not products:
                # Улучшенное сообщение об отсутствии товаров
                return await message.answer(
                    "🔍 <b>Товары не найдены</b>\n\n"
                    f"К сожалению, товары по запросу <code>{search_term}</code> не найдены.\n\n"
                    "• Проверьте правильность написания\n"
                    "• Попробуйте использовать более общие ключевые слова\n"
                    "• Воспользуйтесь поиском по артикулу или категории",
                    parse_mode="HTML",
                    reply_markup=product_not_found_kb()
                )
            
            # Если найден только один товар, показываем его детально
            if len(products) == 1:
                product = products[0]
                
                # Проверяем избранное
                fav_stmt = select(Favorite).where(
                    Favorite.user_id == user_id,
                    Favorite.product_id == product.id
                )
                favorite = session.scalars(fav_stmt).first()
                is_favorite = favorite is not None
                
                # Формируем подробное описание товара
                product_info = (
                    f"<b>{product.name}</b>\n\n"
                    f"📋 <b>Информация о товаре:</b>\n"
                    f"📊 Артикул: {product.vendor_code}\n"
                    f"💰 Цена: {product.price} руб.\n"
                    f"🏭 Производитель: {product.vendor}\n"
                    f"📦 Наличие: {product.availability}\n\n"
                )
                
                if product.description:
                    product_info += f"📝 <b>Описание:</b>\n{product.description[:300]}{'...' if len(product.description) > 300 else ''}\n\n"
                
                # Отправляем фото с описанием товара
                return await message.answer_photo(
                    photo=product.image,
                    caption=product_info,
                    reply_markup=product_kb(product.id, is_fav=is_favorite),
                    parse_mode="HTML"
                )
            else:
                # Если найдено несколько товаров, показываем список
                search_results = f"🔍 <b>Результаты поиска по запросу «{search_term}»:</b>\n\n"
                
                kb = InlineKeyboardBuilder()

                for i, product in enumerate(products, 1):
                    search_results += (
                        f"{i}. <b>{product.name}</b>\n"
                        f"   Артикул: {product.vendor_code}\n"
                        f"   Цена: {product.price} руб.\n\n"
                    )
                    
                    # Добавляем кнопку для просмотра товара
                    kb.button(
                        text=f"👁 Товар #{i}", 
                        callback_data=f"view_product_{product.id}"
                    )
                
                # Добавляем навигационные кнопки
                kb.button(text="🔍 Новый поиск", callback_data="search")
                kb.button(text="🏠 Главное меню", callback_data="main_page")
                
                # Настраиваем расположение кнопок
                kb.adjust(1)
                                
                return await message.answer(
                    search_results,
                    reply_markup=kb.as_markup(),
                    parse_mode="HTML"
                )
            
        except Exception as e:
            logger.error(f"Ошибка при поиске товара по названию: {e}")
            return await message.answer(
                "😔 Произошла ошибка при поиске товаров. Пожалуйста, попробуйте снова позже.",
                reply_markup=main_kb()
            )

# Обработчик для просмотра товара из результатов поиска
@dp.callback_query(F.data.startswith("view_product_"))
async def view_product_handler(callback: CallbackQuery):
    await callback.answer('')
    product_id = str(callback.data).split("_")[2]
    
    try:
        with Session(engine) as session:
            stmt = select(Product).where(Product.id == product_id)
            product = session.scalars(stmt).first()
            
            if not product:
                await callback.message.answer("Товар не найден", reply_markup=main_kb())
                return
            
            # Проверяем, добавлен ли товар в избранное
            fav_stmt = select(Favorite).where(
                Favorite.user_id == callback.from_user.id,
                Favorite.product_id == product.id
            )
            favorite = session.scalars(fav_stmt).first()
            is_favorite = favorite is not None
            
            # Формируем подробное описание товара
            product_info = (
                f"<b>{product.name}</b>\n\n"
                f"📋 <b>Информация о товаре:</b>\n"
                f"📊 Артикул: {product.vendor_code}\n"
                f"💰 Цена: {product.price} руб.\n"
                f"🏭 Производитель: {product.vendor}\n"
                f"📦 Наличие: {product.availability}\n\n"
            )
            
            if product.description:
                product_info += f"📝 <b>Описание:</b>\n{product.description[:300]}{'...' if len(product.description) > 300 else ''}\n\n"
            
            product_info += f"⚙️ Модель: {product.model}\n"
            
            if product.is_bestseller:
                product_info += "🔥 <b>ХИТ ПРОДАЖ!</b>\n\n"
            
            # Отправляем фото с описанием товара
            return await callback.message.answer_photo(
                photo=product.image,
                caption=product_info,
                reply_markup=product_kb(product.id, is_fav=is_favorite),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при просмотре товара: {e}")
        await callback.message.answer(
            "Произошла ошибка при просмотре товара", 
            reply_markup=main_kb()
        )
        
# MARK: add_fav_
        
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
        
        return await callback.answer("Товар успешно добавлен!", reply_markup=main_kb())
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в избранное: {e}")
        return await callback.answer("Ошибка при добавлении товара в избранное!")

# MARK: remove_fav_

@dp.callback_query(F.data.startswith("remove_fav_"))
async def add_product_to_favorites(callback: CallbackQuery):
    
    await callback.answer('')
    try:
        with Session(engine) as session:
            fav = session.query(Favorite).filter(
                Favorite.user_id == callback.from_user.id,
                Favorite.product_id == str(callback.data).split("_")[2]
            ).first()
            if fav:
                session.delete(fav)
                session.commit()
        
        return callback.message.answer("Товар успешно добавлен!", reply_markup=main_kb())
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в избранное: {e}")
        return callback.message.answer("Ошибка при добавлении товара в избранное!")

# MARK: favorites

@dp.callback_query(F.data == 'favorites')
async def favorites_list(callback: CallbackQuery):
    await callback.answer('')
    user_id: int = callback.from_user.id
    
    try:
        with Session(engine) as session:
            stmt = select(Product, Favorite).join(
                Favorite, Favorite.product_id == Product.id
            ).where(Favorite.user_id == user_id)
            
            results = session.execute(stmt).all()
            
            if not results:
                await callback.message.answer(
                    "🔍 В вашем списке избранного пока ничего нет.\n\n"
                    "Добавляйте товары в избранное, чтобы быстро находить их позже!",
                    reply_markup=main_kb()
                )
                return
            
            message = (
                "⭐ <b>Ваши избранные товары</b> ⭐\n\n"
                "Вы можете просмотреть детали товара или добавить его в корзину.\n\n"
            )

            await callback.message.answer(
                message,
                reply_markup=favorite_kb(results),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении избранных товаров: {e}")
        await callback.message.answer(
            "😔 Извините, произошла ошибка при получении избранных товаров. Пожалуйста, попробуйте позже.",
            reply_markup=main_kb()
        )

# MARK: profile

@dp.callback_query(F.data == 'profile')
async def profile_page(callback: CallbackQuery):
    await callback.answer("")
    logger.info(f"Parsing user {callback.from_user.id} profile page")
    
    try:
        with Session(engine) as session:
            # Получаем информацию о пользователе
            stmt = select(User).where(User.telegram_id == callback.from_user.id)
            user = session.scalars(stmt).first()
            
            if not user:
                return await callback.message.answer(
                    "⚠️ Профиль не найден. Пожалуйста, перезапустите бота командой /start", 
                    reply_markup=main_kb()
                )
            
            # Получаем статистику пользователя
            cart_count = session.query(CartItem).filter(CartItem.user_id == callback.from_user.id).count()
            favorites_count = session.query(Favorite).filter(Favorite.user_id == callback.from_user.id).count()
            orders_count = session.query(Orders).filter(Orders.user_id == callback.from_user.id).count()
            reviews_count = session.query(Reviews).filter(Reviews.user_id == callback.from_user.id).count()
            
            # Определяем статус профиля
            profile_status = "⭐ Премиум" if orders_count > 5 else "🔹 Стандартный"
            
            # Формируем статистику активности
            last_activity = user.created_date.strftime("%d.%m.%Y")
            account_age = (datetime.datetime.now() - user.created_date).days
            
            # Создаем сообщение профиля
            profile_message = (
                f"👤 <b>Профиль пользователя</b>\n\n"
                
                f"📋 <b>Основная информация:</b>\n"
                f"• Имя: {user.name or 'Не указано'}\n"
                f"• Телефон: {user.phone_number or 'Не указан'}\n"
                f"• Адрес: {user.address or 'Не указан'}\n"
                f"• Статус: {profile_status}\n\n"
                
                f"📊 <b>Статистика:</b>\n"
                f"• 🛒 Товаров в корзине: {cart_count}\n"
                f"• ⭐ Избранных товаров: {favorites_count}\n"
                f"• 📦 Оформлено заказов: {orders_count}\n"
                f"• ✍️ Оставлено отзывов: {reviews_count}\n\n"
                
                f"⏱ <b>Активность:</b>\n"
                f"• С нами с: {last_activity}\n"
                f"• Дней с регистрации: {account_age}\n\n"
                
                f"Для изменения данных профиля нажмите кнопку ниже 👇"
            )

            
            return await callback.message.answer(
                profile_message,
                reply_markup=profile_kb(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя: {e}")
        return await callback.message.answer(
            "😔 Произошла ошибка при загрузке профиля. Пожалуйста, попробуйте позже.",
            reply_markup=main_kb()
        )

# MARK: states for profile

# Обработчик для изменения имени
@dp.callback_query(F.data == "edit_name")
async def edit_name_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileForm.name)
    await callback.message.answer("Введите ваше имя:")

# Обработчик для изменения телефона
@dp.callback_query(F.data == "edit_phone")
async def edit_phone_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileForm.phone)
    await callback.message.answer(
        "Введите ваш номер телефона в формате +7XXXXXXXXXX:"
    )

# Обработчик для изменения адреса
@dp.callback_query(F.data == "edit_address")
async def edit_address_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(ProfileForm.address)
    await callback.message.answer(
        "Введите ваш адрес доставки:\n"
        "(город, улица, дом, квартира)"
    )

# Обработчик для сохранения имени
@dp.message(ProfileForm.name)
async def process_name(message: Message, state: FSMContext):
    try:
        with Session(engine) as session:
            user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
            if user:
                user.name = message.text
                session.commit()
                await message.answer(
                    "✅ Имя успешно обновлено!",
                    reply_markup=InlineKeyboardBuilder().button(
                        text="Вернуться в профиль", callback_data="profile"
                    ).as_markup()
                )
            else:
                await message.answer("Пользователь не найден.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении имени: {e}")
        await message.answer("Произошла ошибка при обновлении имени.")
    
    await state.clear()

# Обработчик для сохранения телефона
@dp.message(ProfileForm.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text
    
    # Простая валидация номера телефона
    import re
    if not re.match(r'^\+?[0-9]{10,12}$', phone):
        return await message.answer(
            "❌ Неверный формат номера телефона. Пожалуйста, введите номер в формате +7XXXXXXXXXX:",
            reply_markup=InlineKeyboardBuilder().button(
                text="Отмена", callback_data="profile"
            ).as_markup()
        )
    
    try:
        with Session(engine) as session:
            user = session.query(User).filter(User.telegram_id == message.from_user.id).first()
            if user:
                user.phone_number = phone
                session.commit()
                await message.answer(
                    "✅ Номер телефона успешно обновлен!",
                    reply_markup=InlineKeyboardBuilder().button(
                        text="Вернуться в профиль", callback_data="profile"
                    ).as_markup()
                )
            else:
                await message.answer("Пользователь не найден.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении телефона: {e}")
        await message.answer("Произошла ошибка при обновлении телефона.")
    
    await state.clear()

# MARK: cart

@dp.callback_query(F.data == 'cart')
async def cart_page(callback: CallbackQuery):
    await callback.answer('')
    user_id: int = callback.from_user.id
    
    try:
        with Session(engine) as session:
            stmt = select(Product).join(CartItem).where(CartItem.user_id == user_id)
            products = session.scalars(stmt).all()
            
            if not products:
                await callback.message.answer("Ваша корзина пуста", reply_markup=main_kb())
                return
            
            message = "Товары в вашей корзине:\n\n"
            for product in products:
                message += f"🔹 {product.name} - {product.price} руб.\n"
            
            await callback.message.answer(message)
            
    except Exception as e:
        logger.error(f"Ошибка при получении избранных товаров: {e}")
        await callback.message.answer("Ошибка при получении избранных товаров")

# MARK: orders

@dp.callback_query(F.data == 'orders')
async def orders_list(callback: CallbackQuery):
    await callback.answer('')
    user_id: int = callback.from_user.id
    
    try:
        with Session(engine) as session:
            stmt = select(Orders, Product).join(
                Product, Orders.product_id == Product.id
            ).where(Orders.user_id == user_id).order_by(Orders.created_date.desc())
            
            results = session.execute(stmt).all()
            
            if not results:
                return await callback.message.answer(
                    "📭 <b>Список заказов пуст</b>\n\n"
                    "У вас пока нет оформленных заказов.\n"
                    "Воспользуйтесь поиском, чтобы оформить свой первый заказ!",
                    parse_mode="HTML",
                    reply_markup=main_kb()
                )
            

            orders_by_date = {}
            total_spent = 0
            
            for order, product in results:
                # Форматируем дату для группировки
                order_date = order.created_date.strftime('%d.%m.%Y')
                if order_date not in orders_by_date:
                    orders_by_date[order_date] = []
                
                orders_by_date[order_date].append((order, product))
                total_spent += order.summ
            
            # Формируем сообщение со списком заказов
            message = (
                "📦 <b>История ваших заказов</b>\n\n"
                f"Всего заказов: <b>{len(results)}</b>\n"
                f"На сумму: <b>{total_spent:.2f} руб.</b>\n\n"
            )
            
            # Отправляем сообщение с форматированием HTML
            return await callback.message.answer(
                message,
                reply_markup=orders_kb(orders_by_date),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении заказов пользователя {user_id}: {e}")
        return await callback.message.answer(
            "😔 Произошла ошибка при загрузке заказов. Пожалуйста, попробуйте позже.",
            reply_markup=main_kb()
        )

# # Вспомогательная функция для определения статуса заказа
# def get_order_status(order):
#     # В будущем можно добавить логику определения статуса заказа
#     # Например, на основе даты создания или специального поля в базе данных
#     days_since_order = (datetime.datetime.now() - order.created_date).days
    
#     if days_since_order < 1:
#         return "✅ Принят в обработку"
#     elif days_since_order < 3:
#         return "🚚 В пути"
#     elif days_since_order < 5:
#         return "📦 Доставлен"
#     else:
#         return "✓ Завершен"
        
@dp.callback_query(F.data.startswith("order_details_"))
async def order_details_handler(callback: CallbackQuery):
    await callback.answer('')
    order_id = str(callback.data).split("_")[2]
    
    try:
        with Session(engine) as session:
            # Получаем детальную информацию о заказе
            stmt = select(Orders, Product, User).join(
                Product, Orders.product_id == Product.id
            ).join(
                User, Orders.user_id == User.telegram_id
            ).where(Orders.id == order_id)
            
            result = session.execute(stmt).first()
            
            if not result:
                return await callback.message.answer(
                    "Заказ не найден или был удален.",
                    reply_markup=main_kb()
                )
            
            order, product, user = result
            
            # Формируем детальное сообщение о заказе
            order_date = order.created_date.strftime('%d.%m.%Y %H:%M')
            estimated_delivery = (order.created_date + datetime.timedelta(days=5)).strftime('%d.%m.%Y')
            
            message = (
                f"🧾 <b>Заказ #{order.id}</b>\n\n"
                
                f"📋 <b>Информация о заказе:</b>\n"
                f"• Дата заказа: {order_date}\n"
                f"• Ожидаемая доставка: {estimated_delivery}\n\n"
                
                f"🛍 <b>Товар:</b>\n"
                f"• Наименование: {product.name}\n"
                f"• Артикул: {product.vendor_code}\n"
                f"• Цена за ед.: {product.price:.2f} руб.\n"
                f"• Количество: {order.quantity} шт.\n"
                f"• Сумма заказа: {order.summ:.2f} руб.\n\n"
                
                f"📦 <b>Информация о доставке:</b>\n"
                f"• Адрес: {user.address or 'Не указан'}\n"
                f"• Телефон: {user.phone_number or 'Не указан'}\n"
                f"• Получатель: {user.name or 'Не указан'}\n\n"
                
                f"При возникновении вопросов по заказу свяжитесь с нашей службой поддержки."
            )
            
            # Создаем клавиатуру для действий с заказом
            kb = InlineKeyboardBuilder()
            
            # Если заказ недавно создан, добавляем кнопку отмены
            if (datetime.datetime.now() - order.created_date).days < 1:
                kb.button(text="❌ Отменить заказ", callback_data=f"cancel_order_{order.id}")
            
            kb.button(text="🔄 Повторить заказ", callback_data=f"repeat_order_{order.id}")
            kb.button(text="📱 Связаться с менеджером", callback_data="contact_manager")
            kb.button(text="🔙 К списку заказов", callback_data="orders")
            kb.button(text="🏠 Главное меню", callback_data="main_page")
            
            # Настраиваем расположение кнопок
            kb.adjust(1)
            
            # Отправляем изображение товара с детальной информацией о заказе
            return await callback.message.answer_photo(
                photo=product.image,
                caption=message,
                reply_markup=kb.as_markup(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении информации о заказе {order_id}: {e}")
        return await callback.message.answer(
            "Произошла ошибка при загрузке информации о заказе. Пожалуйста, попробуйте позже.",
            reply_markup=main_kb()
        )
    
# MARK: help
@dp.callback_query(F.data == 'help')
async def help_page(callback: CallbackQuery):
    await callback.answer("")
    
    help_message = (
        "🆘 <b>Центр поддержки MDM</b> 🆘\n\n"
        
        "У вас возникли вопросы или нужна помощь? Мы всегда на связи!\n\n"
        
        "📞 <b>Телефон поддержки:</b>\n"
        "8 (800) 123-45-67 (круглосуточно)\n\n"
        
        "✉️ <b>Электронная почта:</b>\n"
        "support@mdm-store.ru\n\n"
        
        "💬 <b>Telegram поддержка:</b>\n"
        "@mdm_support\n\n"
        
        "📝 <b>Часто задаваемые вопросы:</b>\n"
        "• Как оформить заказ?\n"
        "• Какие способы доставки доступны?\n"
        "• Как отследить заказ?\n"
        "• Условия возврата товара\n\n"
        
        "⏱ <b>Время работы офиса:</b>\n"
        "Пн-Пт: 9:00 - 18:00\n"
        "Сб-Вс: выходные\n\n"
        
        "Выберите удобный способ связи ниже 👇"
    )
    
    return await callback.message.edit_text(
        help_message, 
        parse_mode="HTML",
        reply_markup=help_kb(callback.from_user.id)
    )
async def main() -> None:
    create_tables()
    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(filename='mdm.log', level=logging.INFO)
    logger.info('Started')
    tprint("MDMBOT")
    asyncio.run(main())