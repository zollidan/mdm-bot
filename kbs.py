from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
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

