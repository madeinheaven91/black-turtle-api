from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, KeyboardButton, Message,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)
from aiogram.utils.keyboard import (InlineKeyboardBuilder, KeyboardBuilder,
                                    ReplyKeyboardBuilder)

from src.dispatcher import *
from src.state_machines import *

default_builder = ReplyKeyboardBuilder()
default_builder.add(KeyboardButton(text=f"Пары"))
default_builder.add(KeyboardButton(text=f"Пары завтра"))
default_builder.add(KeyboardButton(text="Помощь"))
default_builder.adjust(2)
default_kb = default_builder.as_markup(resize_keyboard=True)

help_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Техподдержка", url="tg://user?id=2087648271")]
    ]
)

registration_end_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="registration_end")]
    ]
)

greeting_builder = InlineKeyboardBuilder()
greeting_builder.add(InlineKeyboardButton(text="Да, давай!", callback_data="yes"))
greeting_builder.add(InlineKeyboardButton(text="Нет, спасибо.", callback_data="no"))
greeting_kb = greeting_builder.as_markup(resize_keyboard=True)
