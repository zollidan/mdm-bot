from sqlalchemy import select
from mdm_bot.core import Product


def format_price(price: float) -> str:
    """Format price for display"""
    return f"{price:.2f} руб."


def format_product_card(product) -> str:
    """
    Format product information as a card

    Args:
        product: Product model instance

    Returns:
        Formatted product information as HTML string
    """
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

    return product_info


def format_main_page_text(user, cart_count: int, favorites_count: int, orders_count: int) -> str:
    """
    Format main page text with user statistics

    Args:
        user: User model instance
        cart_count: Number of items in cart
        favorites_count: Number of favorite products
        orders_count: Number of active orders

    Returns:
        Formatted main page text as HTML string
    """
    # Personalized greeting
    greeting = f"👋 Здравствуйте, {user.name}!" if user else "👋 Здравствуйте!"

    main_page_text = (
        f"{greeting}\n\n"
        f"🛍 <b>MDM Store - ваш надежный поставщик</b>\n\n"
        f"📊 <b>Ваша статистика:</b>\n"
        f"🛒 Товаров в корзине: {cart_count}\n"
        f"⭐ Избранных товаров: {favorites_count}\n"
        f"📦 Активных заказов: {orders_count}\n\n"
        f"• Бесплатная доставка при заказе от 5000 руб.\n\n"
        f"Выберите действие на клавиатуре ниже 👇"
    )
    return main_page_text


async def update_product_card_message(callback, product_id: int, session):
    """
    Update product card in message

    Args:
        callback: CallbackQuery from button press
        product_id: Product ID to update
        session: SQLAlchemy session
    """
    from .keyboards import get_product_keyboard

    # Get product information
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if product:
        product_info = format_product_card(product)

        # Update message with new keyboard
        await callback.message.edit_caption(
            caption=product_info,
            reply_markup=await get_product_keyboard(
                product_id=product.id, session=session, user_id=callback.from_user.id),
            parse_mode="HTML"
        )
