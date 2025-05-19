import asyncio
import datetime
import logging
from aiogram import F, Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from art import tprint

from models import Favorite, OrderItems, User, Product, CartItem, Orders, Reviews
from database import *
from kbs import *
from config import settings
from utils import *

"""
✅ F.data == "main_page" - Обработчик главной страницы
✅ F.data == "search" - Обработчик поиска
✅ F.data == "search_by_name" - Обработчик поиска по названию
✅ F.data.startswith("view_product_") - Просмотр товара
✅ F.data == "favorites" - Страница избранных товаров
✅ F.data.startswith("add_fav_") - Добавление товара в избранное
✅ F.data.startswith("remove_fav_") - Удаление из избранного
✅ F.data == "profile" - Страница профиля
✅ F.data == "edit_name" - Изменение имени
✅ F.data == "edit_phone" - Изменение телефона
✅ F.data == "edit_address" - Изменение адреса
✅ F.data == "cart" - Страница корзины
✅ F.data.startswith("add_cart_") - Добавление товара в корзину
✅ F.data.startswith("remove_cart_") - Удаление из корзины
✅❌ F.data == "orders" - Список заказов
✅ F.data.startswith("order_details_") - Детали заказа
✅ F.data == "help" - Страница помощи
❌ F.data == "edit_profile" - Редактирование профиля (в меню профиля)
❌ F.data.startswith("decrease_qty_") - Уменьшение количества товара в корзине
❌ F.data.startswith("increase_qty_") - Увеличение количества товара в корзине
❌ F.data.startswith("cart_qty_info_") - Информация о количестве товара
❌ F.data == "clear_cart" - Очистка корзины
✅ F.data == "checkout" - Оформление заказа
❌ F.data.startswith("cancel_order_") - Отмена заказа
❌ F.data.startswith("repeat_order_") - Повторение заказа
❌ F.data == "contact_manager" - Связь с менеджером
❌ F.data.startswith("specs_") - Характеристики товара
❌ F.data.startswith("reviews_") - Отзывы о товаре
❌ F.data.startswith("write_review_") - Написание отзыва
❌ F.data == "track_delivery" - Отслеживание доставки
❌ F.data.startswith("remove_all_cart_") - Полное удаление товара из корзины
"""


logger = logging.getLogger(__name__)
dp = Dispatcher()

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
    
    with Session() as session:
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
        with Session() as session:
            user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
            cart_count = session.query(CartItem).filter(CartItem.user_id == callback.from_user.id).count()
            favorites_count = session.query(Favorite).filter(Favorite.user_id == callback.from_user.id).count()
            orders_count = session.query(Orders).filter(Orders.user_id == callback.from_user.id).count()

            main_page_text = make_main_page_text(user, cart_count, favorites_count, orders_count)
            
            return await callback.message.edit_text(
                main_page_text, 
                reply_markup=main_kb(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при загрузке главной страницы: {e}")
        return await callback.message.answer(
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
        
# MARK: search_by_name

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
        
# MARK: search_by_code
# Обработчик для поиска по артикулу
@dp.message(SearchForm.vendor_code_search)
async def process_vendor_code_search(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    vendor_code = message.text
    
    await state.clear()  # Очищаем состояние после получения данных
    
    with Session() as session:
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
            
            # Формируем подробное описание товара
            product_info = make_product_card(product)
            
            # Отправляем фото с описанием товара
            return await message.answer_photo(
                photo=product.image,
                caption=product_info,
                reply_markup=product_kb(product_id=product.id, user_id=message.from_user.id, session=session),
                parse_mode="HTML"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при поиске товара: {e}")
            return await message.answer(
                "😔 Произошла ошибка при поиске товара. Пожалуйста, попробуйте снова позже.",
                reply_markup=main_kb()
            )
        
# MARK: search_by_name
# Обработчик для поиска по названию
@dp.message(SearchForm.name_search)
async def process_name_search(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    search_term = message.text
    
    await state.clear()  # Очищаем состояние после получения данных
    
    with Session() as session:
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
                
                # Формируем подробное описание товара
                product_info = make_product_card(product)
                
                # Отправляем фото с описанием товара
                return await message.answer_photo(
                    photo=product.image,
                    caption=product_info,
                    reply_markup=product_kb(product_id=product.id, user_id=message.from_user.id, session=session),
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

# MARK: view_product_

# Обработчик для просмотра товара из результатов поиска
@dp.callback_query(F.data.startswith("view_product_"))
async def view_product_handler(callback: CallbackQuery):
    await callback.answer('')
    product_id = str(callback.data).split("_")[2]
    
    try:
        with Session() as session:
            stmt = select(Product).where(Product.id == product_id)
            product = session.scalars(stmt).first()
            
            if not product:
                await callback.message.answer("Товар не найден", reply_markup=main_kb())
                return
        
            # Формируем подробное описание товара
            product_info = make_product_card(product)
            
            # Отправляем фото с описанием товара
            return await callback.message.answer_photo(
                photo=product.image,
                caption=product_info,
                reply_markup=product_kb(product.id, user_id=callback.from_user.id, session=session),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при просмотре товара: {e}")
        await callback.message.answer(
            "Произошла ошибка при просмотре товара", 
            reply_markup=main_kb()
        )

# MARK: favorites

@dp.callback_query(F.data == 'favorites')
async def favorites_list(callback: CallbackQuery):
    await callback.answer('')
    user_id: int = callback.from_user.id
    
    try:
        with Session() as session:
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
            
            answer_message = (
                "⭐ <b>Ваши избранные товары</b> ⭐\n\n"
                "Вы можете просмотреть детали товара или добавить его в корзину.\n\n"
            )
            
            for a in enumerate(results, 1):
                print(a)
            
            kb = InlineKeyboardBuilder()

            for i, (product, favorite) in enumerate(results, 1):
                answer_message += (
                    f"{i}. <b>{product.name}</b>\n"
                    f"   Артикул: {product.vendor_code}\n"
                    f"   Цена: {product.price} руб.\n\n"
                )
                
                # Добавляем кнопку для просмотра товара
                kb.button(
                    text=f"👁 Товар #{i}", 
                    callback_data=f"view_product_{product.id}"
                )
            
            kb.button(text="🏠 Главное меню", callback_data="main_page")
        
            kb.adjust(1)
                            
            return await callback.message.answer(
                answer_message,
                reply_markup=kb.as_markup(),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении избранных товаров: {e}")
        await callback.message.answer(
            "😔 Извините, произошла ошибка при получении избранных товаров. Пожалуйста, попробуйте позже.",
            reply_markup=main_kb()
        )
        
# MARK: add_fav_

@dp.callback_query(F.data.startswith("add_fav_"))
async def add_product_to_favorites(callback: CallbackQuery):
    product_id = str(callback.data).split("_")[2]
    
    try:
        with Session() as session:
            # Проверяем, не добавлен ли уже товар в избранное
            existing = session.query(Favorite).filter(
                Favorite.user_id == callback.from_user.id,
                Favorite.product_id == product_id
            ).first()
                        
            if not existing:
                # Добавляем в избранное
                fav = Favorite(
                    user_id=callback.from_user.id,
                    product_id=product_id
                )
                session.add(fav)
                session.commit()
                
                # Получаем информацию о товаре для обновления сообщения
                await update_product_card(callback=callback, product_id=product_id, session=session)
                    
                await callback.answer("✅ Товар добавлен в избранное!")
            else:
                await callback.answer("❗ Товар уже в избранном")
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в избранное: {e}")
        await callback.answer("❌ Ошибка при добавлении товара в избранное")

# MARK: remove_fav_

@dp.callback_query(F.data.startswith("remove_fav_"))
async def remove_from_favorites(callback: CallbackQuery):
    product_id = str(callback.data).split("_")[2]
    
    try:
        with Session() as session:
            # Ищем запись в избранном
            fav = session.query(Favorite).filter(
                Favorite.user_id == callback.from_user.id,
                Favorite.product_id == product_id
            ).first()
            
            if fav:
                session.delete(fav)
                session.commit()
                
                # Получаем информацию о товаре для обновления сообщения
                await update_product_card(callback=callback, product_id=product_id, session=session)
                    
                await callback.answer("✅ Товар удален из избранного")
            else:
                await callback.answer("❗ Товар не был в избранном")
    except Exception as e:
        logger.error(f"Ошибка при удалении товара из избранного: {e}")
        await callback.answer("❌ Ошибка при удалении из избранного")
        
# MARK: profile

@dp.callback_query(F.data == 'profile')
async def profile_page(callback: CallbackQuery):
    await callback.answer("")
    logger.info(f"Parsing user {callback.from_user.id} profile page")
    
    try:
        with Session() as session:
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
        with Session() as session:
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
        with Session() as session:
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
        with Session() as session:
            # Получаем товары в корзине вместе с их количеством
            stmt = select(Product, CartItem).join(
                CartItem, CartItem.product_id == Product.id
            ).where(CartItem.user_id == user_id)
            
            results = session.execute(stmt).all()
            
            if not results:
                return await callback.message.answer(
                    "🛒 <b>Ваша корзина пуста</b>\n\n"
                    "Добавьте товары в корзину, чтобы оформить заказ.\n"
                    "Воспользуйтесь поиском, чтобы найти интересующие вас товары!",
                    parse_mode="HTML",
                    reply_markup=empty_cart_kb()
                )
            
            # Подсчитываем общую сумму и количество товаров
            total_price = 0
            total_items = 0
            
            cart_message = "🛒 <b>Корзина</b>\n\n"
            
            # Формируем список товаров
            for i, (product, cart_item) in enumerate(results, 1):
                item_total = product.price * cart_item.quantity
                total_price += item_total
                total_items += cart_item.quantity
                
                cart_message += (
                    f"{i}. <b>{product.name}</b>\n"
                    f"   Артикул: {product.vendor_code}\n"
                    f"   Цена: {product.price} руб. × {cart_item.quantity} шт. = {item_total} руб.\n\n"
                )
            
            # Добавляем итоговую информацию
            cart_message += (
                f"📊 <b>Итого:</b>\n"
                f"• Товаров: {total_items} шт.\n"
                f"• Сумма: {total_price:.2f} руб.\n\n"
                f"Для управления количеством или удаления товара используйте кнопки ниже."
            )
            
            return await callback.message.answer(
                cart_message,
                reply_markup=cart_kb(results=results),
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении корзины: {e}")
        await callback.message.answer(
            "😔 Извините, произошла ошибка при загрузке корзины. Пожалуйста, попробуйте позже.",
            reply_markup=main_kb()
        )

# MARK: add_cart_

@dp.callback_query(F.data.startswith("add_cart_"))
async def add_product_to_cart(callback: CallbackQuery):
    product_id = str(callback.data).split("_")[2]
    
    try:
        with Session() as session:
            # Проверяем, есть ли уже этот товар в корзине
            existing = session.query(CartItem).filter(
                CartItem.user_id == callback.from_user.id,
                CartItem.product_id == product_id
            ).first()
            
            if not existing:
                # Добавляем товар в корзину
                cart_item = CartItem(
                    user_id=callback.from_user.id,
                    product_id=product_id,
                    quantity=1
                )
                session.add(cart_item)
                session.commit()
                
                # Получаем информацию о товаре для обновления сообщения
                await update_product_card(callback=callback, product_id=product_id, session=session)
                
                await callback.answer("✅ Товар добавлен в корзину!")
            else: 
                pass
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в корзину: {e}")
        await callback.answer("❌ Ошибка при добавлении товара в корзину")

# MARK: remove_cart_

@dp.callback_query(F.data.startswith("remove_cart_"))
async def remove_product_from_cart(callback: CallbackQuery):
    product_id = str(callback.data).split("_")[2]
    
    try:
        with Session() as session:
            # Ищем товар в корзине
            cart_item = session.query(CartItem).filter(
                CartItem.user_id == callback.from_user.id,
                CartItem.product_id == product_id
            ).first()
            
            if cart_item:

                session.delete(cart_item)
                session.commit()
        
                # Получаем информацию о товаре для обновления сообщения
                await update_product_card(callback=callback, product_id=product_id, session=session)
                
                await callback.answer("✅ Товар удален из корзины")
            else:
                await callback.answer("❗ Товара нет в корзине")
    except Exception as e:
        logger.error(f"Ошибка при удалении товара из корзины: {e}")
        await callback.answer("❌ Ошибка при удалении товара из корзины")

# MARK: checkout

@dp.callback_query(F.data == "checkout")
async def checkout_handler(callback: CallbackQuery):
    try:
        with Session() as session:
            # Получаем данные пользователя
            user_data = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
            if not user_data:
                await callback.answer("❌ Ошибка: пользователь не найден")
                return
            
            # Проверяем наличие обязательных данных
            missing_fields = []
            if not user_data.name or user_data.name == "":
                missing_fields.append("имя")
            if not user_data.phone_number or user_data.phone_number == "":
                missing_fields.append("номер телефона")
            if not user_data.address or user_data.address == "":
                missing_fields.append("адрес доставки")
            
            # Если есть отсутствующие поля, предлагаем их заполнить
            if missing_fields:
                missing_text = ", ".join(missing_fields)
                await callback.message.answer(
                    f"⚠️ <b>Для оформления заказа необходимо указать: {missing_text}</b>\n\n"
                    f"Пожалуйста, заполните недостающие данные в вашем профиле.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardBuilder()
                        .button(text="📝 Заполнить профиль", callback_data="profile")
                        .button(text="🔙 Вернуться в корзину", callback_data="cart")
                        .adjust(1)
                        .as_markup()
                )
                return
            
            # Получаем содержимое корзины пользователя
            cart_items = session.query(CartItem, Product).join(
                Product, CartItem.product_id == Product.id
            ).filter(CartItem.user_id == callback.from_user.id).all()
            
            if not cart_items:
                await callback.answer("❌ Ваша корзина пуста!")
                await callback.message.answer(
                    "🛒 <b>Ваша корзина пуста</b>\n\n"
                    "Добавьте товары в корзину, чтобы оформить заказ.",
                    parse_mode="HTML",
                    reply_markup=empty_cart_kb()
                )
                return
            
            # Подсчитываем общую сумму и количество товаров
            total_price = 0
            total_items = 0
            
            order_summary = "🧾 <b>Проверка заказа</b>\n\n"
            
            # Добавляем товары в сообщение
            order_summary += "<b>Товары в заказе:</b>\n"
            for i, (cart_item, product) in enumerate(cart_items, 1):
                item_total = product.price * cart_item.quantity
                total_price += item_total
                total_items += cart_item.quantity
                
                order_summary += (
                    f"{i}. {product.name}\n"
                    f"   {product.price} руб. × {cart_item.quantity} шт. = {item_total} руб.\n"
                )
            
            # Добавляем сводную информацию
            order_summary += (
                f"\n<b>Итого:</b> {total_items} товаров на сумму {total_price:.2f} руб.\n\n"
                
                f"<b>Информация о доставке:</b>\n"
                f"• Получатель: <b>{user_data.name}</b>\n"
                f"• Телефон: <b>{user_data.phone_number}</b>\n"
                f"• Адрес: <b>{user_data.address}</b>\n\n"
                
                f"<b>Способ оплаты:</b> При получении\n\n"
                
                f"Пожалуйста, проверьте данные заказа и подтвердите его оформление."
            )
            
            # Создаем клавиатуру для подтверждения заказа
            kb = InlineKeyboardBuilder()
            kb.button(text="✅ Подтвердить заказ", callback_data="checkout_final")
            kb.button(text="✏️ Изменить данные получателя", callback_data="profile")
            kb.button(text="🔙 Вернуться в корзину", callback_data="cart")
            kb.button(text="❌ Отменить", callback_data="main_page")
            kb.adjust(1)
            
            # Отправляем форму подтверждения заказа
            await callback.message.answer(
                order_summary,
                parse_mode="HTML",
                reply_markup=kb.as_markup()
            )
            
    except Exception as e:
        logger.error(f"Ошибка при оформлении заказа: {e}")
        await callback.answer("❌ Произошла ошибка при оформлении заказа")
        await callback.message.answer(
            "😔 Извините, произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.",
            reply_markup=main_kb()
        )

@dp.callback_query(F.data == "checkout_final")
async def checkout_handler_final(callback: CallbackQuery):
    try:
        with Session() as session:
            # Проверяем данные пользователя еще раз
            user = session.query(User).filter(User.telegram_id == callback.from_user.id).first()
            if not user or not user.name or not user.phone_number or not user.address:
                await callback.answer("❌ Необходимо заполнить данные получателя!")
                return
            
            # Все товары в корзине пользователя
            cart_items = session.query(CartItem).filter(
                CartItem.user_id == callback.from_user.id
            ).all()
            
            if not cart_items:
                await callback.answer("❌ Ваша корзина пуста!")
                return
            
            # Подсчитываем сумму заказа
            total_sum = 0
            for item in cart_items:
                product = session.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    total_sum += product.price * item.quantity
            
            # Создаем новый заказ
            order = Orders(
                user_id=callback.from_user.id,
                total_sum=total_sum,
                status="processing",  # Устанавливаем начальный статус
                delivery_method="Стандартная доставка",  # Можно добавить выбор способа доставки
                payment_method="Оплата при получении"  # Можно добавить выбор способа оплаты
            )
            
            # Добавляем заказ в базу и получаем его ID
            session.add(order)
            session.flush()  # Чтобы получить ID заказа
            
            # Создаем записи OrderItems для каждого товара в заказе
            for item in cart_items:
                product = session.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    order_item = OrderItems(
                        order_id=order.id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        price=product.price  # Сохраняем текущую цену товара
                    )
                    session.add(order_item)
            
            # Очищаем корзину пользователя
            session.query(CartItem).filter(
                CartItem.user_id == callback.from_user.id
            ).delete()
            
            # Сохраняем все изменения
            session.commit()
            
            # Отправляем сообщение об успешном оформлении заказа
            order_message = (
                f"✅ <b>Заказ #{order.id} успешно оформлен!</b>\n\n"
                f"📦 Количество товаров: {sum(item.quantity for item in cart_items)}\n"
                f"💰 Общая сумма: {total_sum:.2f} руб.\n\n"
                
                f"<b>Информация о получателе:</b>\n"
                f"• Имя: {user.name}\n"
                f"• Телефон: {user.phone_number}\n"
                f"• Адрес: {user.address}\n\n"
                
                f"<b>Дальнейшие действия:</b>\n"
                f"• Наш менеджер свяжется с вами для подтверждения заказа\n"
                f"• Статус заказа можно отслеживать в разделе 'Мои заказы'\n\n"
                
                f"Благодарим за покупку в нашем магазине! 🎉"
            )
            
            # Отправляем красивое подтверждение заказа
            kb = InlineKeyboardBuilder()
            kb.button(text="📦 Мои заказы", callback_data="orders")
            kb.button(text="🏠 Главное меню", callback_data="main_page")
            kb.adjust(1, 2)
            
            await callback.message.answer(
                order_message,
                parse_mode="HTML",
                reply_markup=kb.as_markup()
            )
            
            # Отправляем уведомление о новом заказе администратору (если нужно)
            # await bot.send_message(admin_id, f"Новый заказ #{order.id} от {user.name}!")
            
            await callback.answer("✅ Заказ успешно оформлен!")
            
    except Exception as e:
        logger.error(f"Ошибка при оформлении заказа: {e}")
        await callback.answer("❌ Произошла ошибка при оформлении заказа")
        await callback.message.answer(
            "😔 Извините, произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.",
            reply_markup=main_kb()
        )

# MARK: orders
# Переписать страницу заказов, плюс добавить эмодзи
@dp.callback_query(F.data == 'orders')
async def orders_list(callback: CallbackQuery):
    await callback.answer('')
    user_id: int = callback.from_user.id
    
    try:
        with Session() as session:
            # Получаем все заказы пользователя
            orders = session.query(Orders).filter(
                Orders.user_id == user_id
            ).order_by(Orders.order_date.desc()).all()
            
            if not orders:
                return await callback.message.answer(
                    "📭 <b>Список заказов пуст</b>\n\n"
                    "У вас пока нет оформленных заказов.\n"
                    "Воспользуйтесь поиском, чтобы оформить свой первый заказ!",
                    parse_mode="HTML",
                    reply_markup=main_kb()
                )
            
            # Группируем заказы по дате
            orders_by_date = {}
            total_spent = 0
            
            for order in orders:
                # Форматируем дату для группировки
                order_date = order.order_date.strftime('%d.%m.%Y')
                
                if order_date not in orders_by_date:
                    orders_by_date[order_date] = []
                
                # Получаем информацию о товарах в заказе
                order_items = session.query(OrderItems, Product).join(
                    Product, OrderItems.product_id == Product.id
                ).filter(OrderItems.order_id == order.id).all()
                
                # Создаем словарь с информацией о заказе
                order_info = {
                    "order": order,
                    "items": order_items,
                    "items_count": sum(item.quantity for item, _ in order_items),
                    "products_count": len(order_items)
                }
                
                orders_by_date[order_date].append(order_info)
                total_spent += order.total_sum
            
            # Формируем сообщение со списком заказов
            message = (
                "📦 <b>История ваших заказов</b>\n\n"
                f"Всего заказов: <b>{len(orders)}</b>\n"
                f"На сумму: <b>{total_spent:.2f} руб.</b>\n\n"
            )
            
            # Добавляем последние заказы в сообщение
            recent_orders = orders[:3]  # Показываем только 3 последних заказа
            
            if recent_orders:
                message += "<b>Последние заказы:</b>\n\n"
                
                for order in recent_orders:
                    order_date = order.order_date.strftime('%d.%m.%Y %H:%M')
                    
                    # Получаем информацию о товарах в заказе
                    items_count = session.query(OrderItems).filter(
                        OrderItems.order_id == order.id
                    ).with_entities(OrderItems.quantity).all()
                    
                    total_items = sum(item[0] for item in items_count)
                    
                    message += (
                        f"<b>Заказ #{order.id}</b> от {order_date}\n"
                        f"• Товаров: {total_items} шт.\n"
                        f"• Сумма: {order.total_sum:.2f} руб.\n\n"
                    )
            
            # Отправляем сообщение с форматированием HTML и клавиатурой
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

@dp.callback_query(F.data.startswith("order_details_"))
async def order_details_handler(callback: CallbackQuery):
    await callback.answer('')
    order_id = str(callback.data).split("_")[2]
    
    try:
        with Session() as session:
            # Получаем информацию о заказе
            order = session.query(Orders).filter(Orders.id == order_id).first()
            
            if not order:
                return await callback.message.answer(
                    "Заказ не найден или был удален.",
                    reply_markup=main_kb()
                )
            
            # Получаем пользователя
            user = session.query(User).filter(User.telegram_id == order.user_id).first()
            
            # Получаем товары в заказе
            order_items = session.query(OrderItems, Product).join(
                Product, OrderItems.product_id == Product.id
            ).filter(OrderItems.order_id == order.id).all()
            
            if not order_items:
                return await callback.message.answer(
                    "Товары в заказе не найдены.",
                    reply_markup=main_kb()
                )
            
            # Формируем детальное сообщение о заказе
            order_date = order.order_date.strftime('%d.%m.%Y %H:%M')
            estimated_delivery = (order.order_date + datetime.timedelta(days=5)).strftime('%d.%m.%Y')
            
            message = (
                f"<b>Заказ #{order.id}</b>\n\n"
                
                f"📋 <b>Информация о заказе:</b>\n"
                f"• Дата заказа: {order_date}\n"
                f"• Ожидаемая доставка: {estimated_delivery}\n\n"
                
                f"🛍 <b>Товары в заказе:</b>\n"
            )
            
            # Добавляем информацию о каждом товаре
            total_items = 0
            for i, (item, product) in enumerate(order_items, 1):
                message += (
                    f"{i}. {product.name}\n"
                    f"   {product.price:.2f} руб. × {item.quantity} шт. = {item.price * item.quantity:.2f} руб.\n"
                )
                total_items += item.quantity
            
            message += (
                f"\n📊 <b>Итого:</b>\n"
                f"• Товаров: {total_items} шт.\n"
                f"• Сумма заказа: {order.total_sum:.2f} руб.\n\n"
                
                f"📦 <b>Информация о доставке:</b>\n"
                f"• Адрес: {user.address if user and user.address else 'Не указан'}\n"
                f"• Телефон: {user.phone_number if user and user.phone_number else 'Не указан'}\n"
                f"• Получатель: {user.name if user and user.name else 'Не указан'}\n\n"
            )
            
            if order.delivery_method:
                message += f"• Способ доставки: {order.delivery_method}\n"
            
            if order.payment_method:
                message += f"• Способ оплаты: {order.payment_method}\n"
            
            if order.tracking_number:
                message += f"• Трек-номер: {order.tracking_number}\n"
            
            message += "\nПри возникновении вопросов по заказу свяжитесь с нашей службой поддержки."
            
            # Создаем клавиатуру для действий с заказом
            kb = InlineKeyboardBuilder()
            
            # Если заказ в обработке, добавляем кнопку отмены
            if order.status == "processing" or order.status == "confirmed":
                kb.button(text="❌ Отменить заказ", callback_data=f"cancel_order_{order.id}")
            
            kb.button(text="🔄 Повторить заказ", callback_data=f"repeat_order_{order.id}")
            
            # Если есть трек-номер, добавляем кнопку отслеживания
            if order.tracking_number:
                kb.button(text="📍 Отследить заказ", callback_data=f"track_delivery_{order.tracking_number}")
            
            kb.button(text="📱 Связаться с менеджером", callback_data="contact_manager")
            kb.button(text="🔙 К списку заказов", callback_data="orders")
            kb.button(text="🏠 Главное меню", callback_data="main_page")
            
            # Настраиваем расположение кнопок
            kb.adjust(1)
            
            # Получаем первый товар для изображения
            first_product = order_items[0][1] if order_items else None
            
            if first_product and first_product.image:
                # Отправляем изображение первого товара с детальной информацией о заказе
                return await callback.message.answer_photo(
                    photo=first_product.image,
                    caption=message,
                    reply_markup=kb.as_markup(),
                    parse_mode="HTML"
                )
            else:
                # Если изображения нет, отправляем просто текст
                return await callback.message.answer(
                    message,
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
    
# MARK: main

async def main() -> None:
    create_tables()
    bot = Bot(token=settings.BOT_TOKEN)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(filename='mdm.log', level=logging.INFO, encoding='utf-8')
    logger.info('Started')
    tprint("MDMBOT")
    asyncio.run(main())