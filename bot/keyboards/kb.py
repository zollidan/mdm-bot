from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Каталог', callback_data='catalog')
    kb.button(text='Поиск', callback_data='search')
    kb.button(text='Избранное', callback_data='favorites')
    kb.button(text='Заказы', callback_data='orders')
    kb.button(text='Профиль', callback_data='profile')
    kb.button(text='Поддержка', callback_data='support')
    kb.button(text='Оставить отзыв', callback_data='review')
    kb.adjust(1)
    return kb.as_markup()