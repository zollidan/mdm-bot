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
        f"📣 <b>Специальные предложения:</b>\n"
        f"• Скидка 10% на все товары до 30 мая\n"
        f"• Бесплатная доставка при заказе от 5000 руб.\n\n"
        f"Выберите действие на клавиатуре ниже 👇"
    )