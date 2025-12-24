from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from mdm_bot.core import Favorite, CartItem, settings


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Build main menu keyboard with WebApp button"""
    kb = InlineKeyboardBuilder()

    # Web App button for catalog
    webapp_url = getattr(settings, 'WEBAPP_URL', 'https://your-domain.com')
    kb.button(text="🛍️ Открыть каталог", web_app=WebAppInfo(url=webapp_url))

    kb.button(text="🔍 Поиск", callback_data="search")
    kb.button(text="🛒 Моя корзина", callback_data="cart")
    kb.button(text="⭐ Избранное", callback_data="favorites")
    kb.button(text="📦 Мои заказы", callback_data="orders")
    kb.button(text="👤 Профиль", callback_data="profile")
    kb.button(text="❓ Помощь", callback_data="help")

    kb.adjust(1)
    return kb.as_markup()


def get_cart_keyboard(results) -> InlineKeyboardMarkup:
    """Build cart keyboard with product items"""
    kb = InlineKeyboardBuilder()

    for i, (product, cart_item) in enumerate(results, 1):
        # Product name button
        kb.button(
            text=f"{i}. {product.name[:20]}{('...' if len(product.name) > 20 else '')}",
            callback_data=f"view_product_{product.id}"
        )

        # Delete button
        kb.button(
            text="🗑 Удалить",
            callback_data=f"remove_cart_{cart_item.product_id}"
        )

    # Cart action buttons
    kb.button(text="💳 Оформить заказ", callback_data="checkout")
    kb.button(text="🏠 Главное меню", callback_data="main_page")

    kb.adjust(1)
    return kb.as_markup()


def get_product_not_found_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard for product not found page"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🔍 Новый поиск", callback_data="search")
    kb.button(text="🏠 Главное меню", callback_data="main_page")

    kb.adjust(1)
    return kb.as_markup()


async def get_product_keyboard(product_id: int, session, user_id: int) -> InlineKeyboardMarkup:
    """
    Build keyboard for product page with dynamic buttons

    Args:
        product_id: Product ID
        session: SQLAlchemy session
        user_id: Telegram user ID

    Returns:
        Product keyboard markup
    """
    kb = InlineKeyboardBuilder()

    # Check if product in favorites
    fav_result = await session.execute(select(Favorite).where(
        Favorite.user_id == user_id, Favorite.product_id == product_id))
    is_fav = fav_result.scalar_one_or_none() is not None

    # Check if product in cart
    cart_result = await session.execute(select(CartItem).where(
        CartItem.user_id == user_id, CartItem.product_id == product_id))
    is_cart = cart_result.scalar_one_or_none() is not None

    # Cart button
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

    # Favorite button
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

    # Navigation buttons
    kb.button(text="🔍 К поиску", callback_data="search")
    kb.button(text="🏠 Главное меню", callback_data="main_page")

    kb.adjust(1, 1, 2, 2, 2)

    return kb.as_markup()


def get_favorites_keyboard(results):
    """
    Build keyboard for favorites page

    Args:
        results: List of tuples (product, favorite)

    Returns:
        Favorites keyboard markup
    """
    kb = InlineKeyboardBuilder()

    # Group buttons by products
    for i, (product, favorite) in enumerate(results, 1):
        # Product name
        kb.button(
            text=f"{i}. {product.name[:20]}{('...' if len(product.name) > 20 else '')}",
            callback_data=f"view_product_{product.id}"
        )

        # Action buttons
        row = [
            {"text": "👁 Просмотр", "callback_data": f"view_product_{product.id}"},
            {"text": "🛒 В корзину", "callback_data": f"add_cart_{product.id}"},
            {"text": "❌ Удалить", "callback_data": f"remove_fav_{product.id}"}
        ]

        for btn in row:
            kb.button(text=btn["text"], callback_data=btn["callback_data"])

    kb.button(text="🏠 Главное меню", callback_data="main_page")

    kb.adjust(1, 3)

    return kb.as_markup()


def get_orders_keyboard(orders_by_date):
    """
    Build keyboard for orders page

    Args:
        orders_by_date: Dictionary with orders grouped by dates

    Returns:
        Orders keyboard markup
    """
    kb = InlineKeyboardBuilder()

    # Sort dates in reverse order (newest first)
    for date in sorted(orders_by_date.keys(), reverse=True):
        date_orders = orders_by_date[date]

        # Add buttons for each order
        for order_info in date_orders:
            order = order_info["order"]
            items_count = order_info.get("items_count", 0)

            kb.button(
                text=f"Заказ #{order.id} ({items_count} шт., {order.total_sum:.0f} р.)",
                callback_data=f"order_details_{order.id}"
            )

    kb.button(text="🏠 Главное меню", callback_data="main_page")

    kb.adjust(1)
    return kb.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Build profile settings keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="📝 Изменить имя", callback_data="edit_name")
    kb.button(text="📞 Изменить телефон", callback_data="edit_phone")
    kb.button(text="🏠 Изменить адрес", callback_data="edit_address")
    kb.button(text="📊 История заказов", callback_data="orders")
    kb.button(text="🔙 Назад", callback_data="main_page")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def get_help_keyboard(user_telegram_id):
    """Build help page keyboard"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Главное меню", callback_data="main_page")

    kb.adjust(1)
    return kb.as_markup()


def get_empty_cart_keyboard():
    """Build keyboard for empty cart page"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🔍 Поиск товаров", callback_data="search")
    kb.button(text="⭐ Избранное", callback_data="favorites")
    kb.button(text="🏠 Главное меню", callback_data="main_page")
    kb.adjust(2, 1)
    return kb.as_markup()
