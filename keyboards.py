from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Referal"), KeyboardButton(text="Referal soni")]
    ],
    resize_keyboard=True
)

def get_subscribe_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL[1:]}")],
        [InlineKeyboardButton(text="Tekshirish", callback_data="check_subscription")]
    ])
    return kb