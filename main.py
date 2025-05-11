import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from pydantic_settings import BaseSettings
from art import tprint
class Settins(BaseSettings):
    BOT_TOKEN: str

settings = Settins()
logger = logging.getLogger(__name__)
dp = Dispatcher()

def main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Первая кнопка!", callback_data="first_button")

    kb.adjust(2)
    return kb.as_markup()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    
    await message.answer(f"Hello {message.from_user.username}, I am your bot!", reply_markup=main_kb())

async def main() -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(filename='mdm.log', level=logging.INFO)
    logger.info('Started')
    tprint("MDMBOT")
    asyncio.run(main())