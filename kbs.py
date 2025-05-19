from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from models import Favorite, CartItem

# MARK: kbs
# TODO: refactor this file later 

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

def cart_kb(results) -> InlineKeyboardMarkup:
                # Создаем клавиатуру для корзины
            kb = InlineKeyboardBuilder()
            
            for i, (product, cart_item) in enumerate(results, 1):
                # Кнопка с названием товара для просмотра
                kb.button(
                    text=f"{i}. {product.name[:20]}{('...' if len(product.name) > 20 else '')}",
                    callback_data=f"view_product_{product.id}"
                )
            
                # Кнопка удаления
                kb.button(
                    text="🗑 Удалить",
                    callback_data=f"remove_all_cart_{cart_item.product_id}"
                )
            
            # Кнопки действий с корзиной
            kb.button(text="💳 Оформить заказ", callback_data="checkout")
            kb.button(text="🧹 Очистить корзину", callback_data="clear_cart")
            kb.button(text="🏠 Главное меню", callback_data="main_page")
            
            kb.adjust(1)
            return kb.as_markup()

def product_not_found_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔢 Поиск по артикулу", callback_data="search_by_code")
    kb.button(text="📝 Поиск по названию", callback_data="search_by_name")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    
    kb.adjust(2, 2)
    return kb.as_markup()

def product_kb(product_id: int, session, user_id) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для страницы товара.
    
    Args:
        product_id: ID товара
        session: Сессия SQLAlchemy для работы с БД
        user_id: ID пользователя
        is_fav: Находится ли товар в избранном
        is_cart: Находится ли товар в корзине
    
    Returns:
        Клавиатура для товара
    """
    kb = InlineKeyboardBuilder()
    
    # проверка на наличие товара в избранном
    is_fav = session.query(Favorite).filter(Favorite.user_id == user_id, Favorite.product_id == product_id).first() is not None
    is_cart = session.query(CartItem).filter(CartItem.user_id == user_id, CartItem.product_id == product_id).first() is not None
    
    if is_cart:
        kb.button(
            text="❌ Удалить из корзины", 
            callback_data=f"remove_cart_{product_id}"
        )
    else:
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
    
    kb.adjust(1, 1, 2, 2, 2)
    
    return kb.as_markup()

def favorite_kb(results):
    """
    Создает клавиатуру для страницы избранных товаров.
    
    Args:
        results: Список кортежей (product, favorite)
    
    Returns:
        Клавиатура для страницы избранных товаров
    """
    kb = InlineKeyboardBuilder()
    
    # Группируем кнопки по товарам для удобства
    for i, (product, favorite) in enumerate(results, 1):
        # Добавляем номер товара для удобства
        kb.button(
            text=f"{i}. {product.name[:20]}{('...' if len(product.name) > 20 else '')}", 
            callback_data=f"view_product_{product.id}"
        )
        
        # Добавляем кнопки действий
        row = [
            {"text": "👁 Просмотр", "callback_data": f"view_product_{product.id}"},
            {"text": "🛒 В корзину", "callback_data": f"add_cart_{product.id}"},
            {"text": "❌ Удалить", "callback_data": f"remove_fav_{product.id}"}
        ]
        
        # Добавляем кнопки для товара
        for btn in row:
            kb.button(text=btn["text"], callback_data=btn["callback_data"])
    
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    
    # Настраиваем расположение кнопок:
    # Одна кнопка с названием товара в строке
    # Затем три кнопки действий для этого товара
    # Далее следующий товар и т.д.
    kb.adjust(1, 3)
    
    return kb.as_markup()

def orders_kb(orders_by_date):
    """
    Создает клавиатуру для страницы заказов.
    
    Args:
        orders_by_date: Словарь с данными заказов, сгруппированных по датам
    
    Returns:
        InlineKeyboardMarkup: Клавиатура для страницы заказов
    """
    kb = InlineKeyboardBuilder()
    
    # Сортируем даты в обратном порядке (от новых к старым)
    for date in sorted(orders_by_date.keys(), reverse=True):
        date_orders = orders_by_date[date]
        
        # Добавляем заголовок с датой
        kb.button(
            text=f"📅 {date}",
            callback_data=f"date_header_{date.replace('.', '_')}"  # Callback для косметических целей
        )
        
        # Добавляем кнопки для каждого заказа в этот день
        for order_info in date_orders:
            order = order_info["order"]
            items_count = order_info.get("items_count", 0)
            
            kb.button(
                text=f"Заказ #{order.id} ({items_count} шт., {order.total_sum:.0f} р.)", 
                callback_data=f"order_details_{order.id}"
            )
    
    # Добавляем кнопки навигации
    kb.button(text="📱 Связаться с менеджером", callback_data="contact_manager")
    kb.button(text="🔄 Обновить", callback_data="orders")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    
    # Размещаем по одной кнопке в строке
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

def empty_cart_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔍 Поиск товаров", callback_data="search")
    kb.button(text="⭐ Избранное", callback_data="favorites")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    kb.adjust(2, 1)
    return kb.as_markup()