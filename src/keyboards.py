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

reg_group_or_teacher_builder = InlineKeyboardBuilder()
reg_group_or_teacher_builder.add(InlineKeyboardButton(text="Группы", callback_data="reg_group"))
reg_group_or_teacher_builder.add(InlineKeyboardButton(text="Преподавателя", callback_data="reg_teacher"))
reg_group_or_teacher_kb = reg_group_or_teacher_builder.as_markup(resize_keyboard=True)



reg_end_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отмена", callback_data="reg_end")]
    ]
)

greeting_builder = InlineKeyboardBuilder()
greeting_builder.add(InlineKeyboardButton(text="Да, давай!", callback_data="reg_yes"))
greeting_builder.add(InlineKeyboardButton(text="Нет, спасибо.", callback_data="reg_no"))
greeting_kb = greeting_builder.as_markup(resize_keyboard=True)
