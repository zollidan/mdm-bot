from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.dao.dao import FavoriteDAO, ProductDao, UserDAO
from bot.user.kbs import main_user_kb, product_kb
from bot.user.schemas import TelegramIDModel, UserModel

user_router = Router()

class SearchState(StatesGroup):
    user_search_request = State()
    
@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    user_id = message.from_user.id
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=user_id)
    )

    if user_info:
        return await message.answer(
            f"👋 Привет, {message.from_user.full_name}! Выберите необходимое действие",
            reply_markup=main_user_kb()
        )

    values = UserModel(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await UserDAO.add(session=session_with_commit, values=values)
    await message.answer("🎉 <b>Благодарим за регистрацию!</b>. Теперь выберите необходимое действие.",
                         reply_markup=main_user_kb())


@user_router.callback_query(F.data == 'search')
async def search_products(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Введите <b>артикул</b> чтобы найти товар.')

    await state.set_state(SearchState.user_search_request)

    await callback.answer('')

@user_router.message(SearchState.user_search_request)
async def proces_user_search(message: Message, state: FSMContext, session_without_commit: AsyncSession):
    await state.clear()

    vendor_code = message.text.strip()
    
    product = await ProductDao.find_one_or_none_by_vendor_code(vendor_code, session_without_commit)

    if product:
        response = (
            f"<b>Название:</b> {product.name}\n\n"
            f"<b>Описание:</b> {product.description}\n\n"
            f"<b>Цена:</b> {product.price}₽"
        )
        await message.answer(text=response, reply_markup=product_kb(product_id=product.id, price=product.price))
    else:
        await message.answer(text="❌ Товар не найден. Попробуйте снова.", reply_markup=main_user_kb())
        
@user_router.callback_query(F.data == 'favorites')
async def show_favorites(callback: CallbackQuery, session_without_commit: AsyncSession):
    user_id = callback.from_user.id

    user = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=TelegramIDModel(telegram_id=user_id)
    )

    if not user:
        return await callback.message.answer("Пользователь не найден.")

    favorites = await FavoriteDAO.get_user_favorites(user.id, session=session_without_commit)

    if not favorites:
        return await callback.message.answer("У вас нет избранных товаров.", reply_markup=main_user_kb())

    for fav in favorites:
        product = await ProductDao.find_one_or_none_by_id(fav.product_id, session=session_without_commit)
        if product:
            text = f"<b>{product.name}</b>\n{product.description}\nЦена: {product.price} BYN"
            await callback.message.answer(
                text,
                reply_markup=product_kb(product.id, product.price, is_favorite=True)
            )
            

@user_router.callback_query(F.data.startswith("addfav_"))
async def add_to_favorites(callback: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(callback.data.split("_")[1])
    user_telegram_id = callback.from_user.id

    user = await UserDAO.find_one_or_none(session=session_with_commit, filters=TelegramIDModel(telegram_id=user_telegram_id))
    if not user:
        return await callback.answer("Пользователь не найден.")

    await FavoriteDAO.add_favorite(user.id, product_id, session=session_with_commit)
    await callback.answer("Добавлено в избранное ❤️")

    # Обновить карточку
    product = await ProductDao.find_one_or_none_by_id(product_id, session=session_with_commit)
    if product:
        text = f"<b>{product.name}</b>\n{product.description}\nЦена: {product.price} BYN"
        await callback.message.edit_text(text, reply_markup=product_kb(product.id, product.price, is_favorite=True))


@user_router.callback_query(F.data.startswith("removefav_"))
async def remove_from_favorites(callback: CallbackQuery, session_with_commit: AsyncSession):
    product_id = int(callback.data.split("_")[1])
    user_telegram_id = callback.from_user.id

    user = await UserDAO.find_one_or_none(session=session_with_commit, filters=TelegramIDModel(telegram_id=user_telegram_id))
    if not user:
        return await callback.answer("Пользователь не найден.")

    await FavoriteDAO.remove_favorite(user.id, product_id, session=session_with_commit)
    await callback.answer("Удалено из избранного 💔")

    product = await ProductDao.find_one_or_none_by_id(product_id, session=session_with_commit)
    if product:
        text = f"<b>{product.name}</b>\n{product.description}\nЦена: {product.price} BYN"
        await callback.message.edit_text(text, reply_markup=product_kb(product.id, product.price, is_favorite=False))
