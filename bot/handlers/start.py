from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keyboards.kb import main_kb

start_router = Router()

@start_router.message(CommandStart())
async def start_command(message: Message):
    await message.answer('this is first ever route', reply_markup=main_kb())