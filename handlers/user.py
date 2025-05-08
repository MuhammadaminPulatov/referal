from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus
from aiogram import Bot
from database import conn, cursor
from keyboards import main_kb, get_subscribe_kb
from config import CHANNEL

router = Router()

async def is_subscribed(bot: Bot, user_id: int):
    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except:
        return False

@router.message(CommandStart())
async def start_cmd(msg: Message, bot: Bot):
    if not await is_subscribed(bot, msg.from_user.id):
        await msg.answer(
            f"Assalomu alaykum! Botdan foydalanish uchun iltimos, {CHANNEL} kanaliga obuna bo‘ling.",
            reply_markup=get_subscribe_kb()
        )
        return

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (msg.from_user.id,))
    if not cursor.fetchone():
        ref = msg.text.split()[1] if len(msg.text.split()) > 1 else None
        if ref and int(ref) != msg.from_user.id:
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (int(ref),))
            if cursor.fetchone():
                cursor.execute("INSERT INTO users (user_id, full_name, referer_id) VALUES (%s, %s, %s)",
                               (msg.from_user.id, msg.from_user.full_name, int(ref)))
            else:
                cursor.execute("INSERT INTO users (user_id, full_name) VALUES (%s, %s)",
                               (msg.from_user.id, msg.from_user.full_name))
        else:
            cursor.execute("INSERT INTO users (user_id, full_name) VALUES (%s, %s)",
                           (msg.from_user.id, msg.from_user.full_name))
        conn.commit()

    await msg.answer(f"Assalomu alaykum, {msg.from_user.full_name}", reply_markup=main_kb)

@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (callback.from_user.id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (user_id, full_name) VALUES (%s, %s)",
                           (callback.from_user.id, callback.from_user.full_name))
            conn.commit()
        await callback.message.answer(
            f"Assalomu alaykum, {callback.from_user.full_name}",
            reply_markup=main_kb
        )
        await callback.message.delete()
    else:
        await callback.answer("Iltimos, avval kanalga obuna bo‘ling!", show_alert=True)

@router.message(F.text.lower() == "referal")
async def referal_link(msg: Message, bot: Bot):
    if not await is_subscribed(bot, msg.from_user.id):
        await msg.answer(
            f"Iltimos, {CHANNEL} kanaliga obuna bo‘ling.",
            reply_markup=get_subscribe_kb()
        )
        return
    await msg.answer(f"https://t.me/{(await bot.me()).username}?start={msg.from_user.id}")

@router.message(F.text.lower() == "referal soni")
async def referal_count(msg: Message, bot: Bot):
    if not await is_subscribed(bot, msg.from_user.id):
        await msg.answer(
            f"Iltimos, {CHANNEL} kanaliga obuna bo‘ling.",
            reply_markup=get_subscribe_kb()
        )
        return
    cursor.execute("SELECT COUNT(*) FROM users WHERE referer_id = %s", (msg.from_user.id,))
    count = cursor.fetchone()[0]
    await msg.answer(f"Siz orqali {count} ta foydalanuvchi kirgan")

@router.message()
async def unknown(msg: Message, bot: Bot):
    if not await is_subscribed(bot, msg.from_user.id):
        await msg.answer(
            f"Iltimos, {CHANNEL} kanaliga obuna bo‘ling.",
            reply_markup=get_subscribe_kb()
        )
        return
    await msg.answer("Iltimos, menyudan tugma tanlang.")