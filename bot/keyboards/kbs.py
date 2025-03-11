from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎮 Начать игру", callback_data='start_game')
    kb.button(text="🎵 Добавить напев", callback_data='add_hummings')
    kb.button(text="🎤 Мои напевы", callback_data='my_hummings')
    kb.button(text="🏆 Таблица лидеров", callback_data='leader_board')
    kb.button(text="🪪 Профиль", callback_data='profile')
    kb.button(text="❓ Помощь", callback_data='help')
    kb.adjust(1)
    return kb.as_markup()
    
def go_main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🏠 Главное меню", callback_data='home_page')
    kb.adjust(1)
    return kb.as_markup()
