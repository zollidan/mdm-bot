from sqlalchemy import select


from kbs import product_kb
from models import Product


def make_product_card(product):
    # Формируем описание товара
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


def make_main_page_text(user, cart_count, favorites_count, orders_count):
    # Персонализированное приветствие
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


async def update_product_card(callback, product_id, session):
    """
    Обновляет карточку товара в сообщении.

    args: 
        callback: CallbackQuery, полученный из нажатия кнопки
        product_id: ID товара, который нужно обновить
        session: Сессия SQLAlchemy для работы с БД
    returns:
        None
    """
    # Получаем информацию о товаре для обновления сообщения
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if product:
        product_info = make_product_card(product)

        # Обновляем сообщение с новой клавиатурой
        await callback.message.edit_caption(
            caption=product_info,
            reply_markup=await product_kb(
                product_id=product.id, session=session, user_id=callback.from_user.id),
            parse_mode="HTML"
        )
