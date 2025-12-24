import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select

from mdm_bot.core import AsyncSessionFactory, User, settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Handler for /start command.
    Creates or updates user in database and sends Mini App link.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    async with AsyncSessionFactory() as session:
        logger.info(f"User {user_id} started the bot")

        # Check if user exists
        stmt = select(User).where(User.telegram_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            # Create new user
            user = User(
                telegram_id=user_id,
                username=username,
                name=full_name or "",
                phone_number="",
                address=""
            )
            session.add(user)
            await session.commit()
            logger.info(f"New user {user_id} created")
        else:
            # Update username if changed
            if user.username != username:
                user.username = username
                await session.commit()
            logger.info(f"Existing user {user_id} returned")

    # Create Mini App button
    webapp_button = InlineKeyboardButton(
        text="🛍️ Открыть каталог",
        web_app={"url": settings.WEBAPP_URL}
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[webapp_button]])

    welcome_message = (
        f"👋 Привет, {full_name}!\n\n"
        "Добро пожаловать в MDM Bot — ваш магазин в Telegram!\n\n"
        "🔹 Просматривайте каталог товаров\n"
        "🔹 Добавляйте товары в корзину\n"
        "🔹 Оформляйте заказы\n\n"
        "Нажмите кнопку ниже, чтобы открыть каталог 👇"
    )

    await message.answer(
        welcome_message,
        reply_markup=keyboard
    )
