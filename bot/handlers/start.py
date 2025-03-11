
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from bot.base import UserDAO
from bot.keyboards.kbs import main_kb, go_main_kb
from bot.schemas import UserSchema, TelegramIDBase



start_router = Router()

@start_router.message(CommandStart())
async def start_command(message: Message, session_with_commit: AsyncSession):
    
    greeting_text = f"""
🎵 *Добро пожаловать в игру «Угадай мелодию»!* 🎵

Привет, {message.from_user.first_name}! 

В этой игре пользователи сами создают музыкальную базу, напевая известные треки. 

Как играть:
1️⃣ Сначала запишите свой напев для общей библиотеки
2️⃣ Затем угадывайте мелодии, которые напели другие участники
3️⃣ Получайте очки за каждый угаданный трек
4️⃣ Следите за рейтингом своих напевов

Выберите действие на клавиатуре ниже 👇
    """
    

    
    user_id = message.from_user.id
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDBase(telegram_id=user_id)
    )
    
    if user_info:
        return await message.answer(
            f"👋 Привет, {message.from_user.full_name}! Добро пожаловать! Ваш текущий счет {user_info.points} очков!",
            reply_markup=main_kb()
            )   

    values = UserSchema(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    
    await UserDAO.add(session=session_with_commit, values=values)
    await message.answer(greeting_text, reply_markup=main_kb())
   
@start_router.callback_query(F.data == 'home_page')
async def home_page(callback: CallbackQuery):
    
    await callback.answer('')
    
    return await callback.message.answer("Выберите действие на клавиатуре ниже 👇", reply_markup=main_kb())
    
@start_router.callback_query(F.data == "help")
async def help_command(callback: CallbackQuery):
    
    await callback.answer('')
    
    help_text = """
📋 Справка по игре «Угадай мелодию» 📋

Как играть:
1️⃣ *Добавьте свой напев*
   • Нажмите кнопку «🎵 Добавить напев»
   • Запишите голосовое, напевая или насвистывая известную песню
   • Укажите название трека и исполнителя

2️⃣ Угадывайте мелодии
   • Нажмите кнопку «🎮 Начать игру»
   • Прослушайте напев другого пользователя
   • Введите название трека, которое вы угадали
   • За каждый угаданный трек вы получаете очки!

Рейтинги:
• Рейтинг пользователей основан на количестве очков за угаданные песни
• Рейтинг ваших напевов показывает, сколько раз их угадали
• Ежедневно обновляемые рейтинги лучших напевов

Правила:
• Напевайте только узнаваемые части песен
• Не используйте ненормативную лексику
• Не записывайте голос других людей без их согласия
• Если напев кажется неприемлемым, нажмите «Пожаловаться»

Возникли проблемы?
Напишите нам: @admin_user
    """
    
    return await callback.message.answer(help_text, reply_markup=go_main_kb())