from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import settings


def main_user_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👤 Избранное", callback_data="favorites")
    kb.button(text="🛍 Поиск по товарам", callback_data="search")
    kb.button(text="📞  Поддержка", callback_data="support")
    # if user_id in settings.ADMIN_IDS:
    #     kb.button(text="⚙️ Админ панель", callback_data="admin_panel")
    kb.adjust(1)
    return kb.as_markup()

def purchases_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Смотреть покупки", callback_data="purchases")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def product_kb(product_id, price, is_favorite: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💸 Купить", callback_data=f"buy_{product_id}_{price}")
    if is_favorite:
        kb.button(text="❌ Удалить из избранного", callback_data=f"removefav_{product_id}")
    else:
        kb.button(text="⭐ В избранное", callback_data=f"addfav_{product_id}")
    kb.button(text="🏠 На главную", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


def get_product_buy_kb(price) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Оплатить {price}₽', pay=True)],
        [InlineKeyboardButton(text='Отменить', callback_data='home')]
    ])