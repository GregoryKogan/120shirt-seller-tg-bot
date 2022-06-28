from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from config import SIZES


def select_size_keyboard():
    buttons = [[KeyboardButton(size)] for size in SIZES]
    return ReplyKeyboardMarkup(buttons, one_time_keyboard=True)


def select_delivery_type_keyboard():
    buttons = [
        [KeyboardButton("Самовывоз")],
        [KeyboardButton("Доставка")],
    ]
    return ReplyKeyboardMarkup(buttons, one_time_keyboard=True)


def verify_data_keyboard():
    buttons = [
        [KeyboardButton("Все верно")],
        [KeyboardButton("Заполнить данные заново")],
    ]
    return ReplyKeyboardMarkup(buttons, one_time_keyboard=True)


def go_to_payment(amount: float):
    buttons = [[InlineKeyboardButton("Оплатить", callback_data=f"pay {amount}")]]
    return InlineKeyboardMarkup(buttons)
