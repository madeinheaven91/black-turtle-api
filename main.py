import asyncio
import locale
import logging
import re
import sys
from os import getenv

import psycopg2
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dotenv import load_dotenv

from data import *
from src.db import db_commit_close, db_connect
from src.dispatcher import *
from src.handlers import (handle_bell, handle_exception, handle_fio,
                          handle_groups, handle_help, handle_lessons)
from src.keyboards import *
from src.state_machines import *
from src.utils import log_request, safe_message

ignore_messages = False

################
###          ###
### COMMANDS ###
###          ###
################

@router.message(F.text)
async def msg_handler(message: Message) -> None:
    if ignore_messages:
        return
    ## Initialize tokens
    tokens = re.sub(" +", " ", message.text.lower().strip()).split(" ")
    while len(tokens) < 5:
        tokens.append("")

    match tokens[0]:
        case "помощь":
            await log_request(message)
            await handle_exception(handle_help, message, tokens)
        case "пары":
            await log_request(message)
            await handle_exception(handle_lessons, message, tokens)
        case "фио":
            await log_request(message)
            await handle_exception(handle_fio, message, tokens)
        case "звонки":
            await log_request(message)
            await handle_exception(handle_bell, message, tokens)
        case "группы":
            await log_request(message)
            await handle_exception(handle_groups, message, tokens)


@dp.message(Command("kill"))
async def cmd_kill(message: Message) -> None:
    await log_request(message)
    if message.from_user.id == 2087648271:
        await safe_message(message, "Я умер")
        await dp.stop_polling()


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await log_request(message)
    ignore_messages = True

    # Database stuff
    conn, cur = await db_connect()
    cur.execute("""SELECT id from Chat WHERE id=%s""", (message.chat.id,))
    exists = cur.fetchone()

    if exists is None:
        chat_id = message.chat.id
        name = message.chat.title if message.chat.title else message.chat.full_name
        is_group = message.chat.type == "group" or message.chat.type == "supergroup"
        cur.execute(
            """
                INSERT INTO Chat (id, name, is_group)
                VALUES (%s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
                """,
            (chat_id, name, is_group),
        )
    await db_commit_close(conn, cur)

    try:
        await message.answer(
            "Привет! Для начала давай выберем группу, в которой ты учишься.",
            reply_markup=greeting_kb,
        )
    except Exception as e:
        logging.error(e)


@dp.callback_query(F.data == "yes")
async def registration_callback(callback: CallbackQuery, state: FSMContext) -> None:
    ignore_messages = False
    await callback.message.edit_text("Введи номер своей группы")
    await state.set_state(Registration.select)
    await callback.answer()


@dp.callback_query(F.data == "no")
async def process_callback_no(callback: CallbackQuery) -> None:
    ignore_messages = False
    await callback.message.edit_text(
        "Хорошо! Ты можешь зарегистрироваться в другой раз, прописав <b>регистрация</b>.\n\nЧтобы узнать, что я могу, пропиши <b>помощь</b>!",
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@dp.message(Registration.select)
async def select_group(message: Message, state: FSMContext) -> None:
    try:
        group_id = groups_csv[message.text]
    except Exception:
        await state.set_state(Registration.select)
        await message.answer(
            """⚠️ <b>Такой группы нет...</b>

Отправь номер своей группы еще раз.""",
            reply_markup=registration_end_kb,
        )
        return

    conn, cur = await db_connect()
    cur.execute(
        """UPDATE Chat
    SET selected_group_id=%s
    WHERE id=%s""",
        (group_id, message.chat.id),
    )
    await db_commit_close(conn, cur)

    try:
        await message.answer(
            """Отлично, группа выбрана! Теперь вы можете смотреть пары своей группы!\n\nЧтобы узнать, что я могу, пропиши <b>помощь</b>!""",
            parse_mode=ParseMode.HTML,
            reply_markup=default_kb,
        )
    except Exception as e:
        logging.error(e)

    await state.clear()


@dp.message(F.text.lower() == "регистрация")
async def registration(message: Message, state: FSMContext) -> None:
    await message.answer("Введи номер своей группы")
    await state.set_state(Registration.select)


@dp.callback_query(F.data == "registration_end")
async def process_callback_exit(callback: CallbackQuery, state: FSMContext) -> None:
    ignore_messages = False
    await state.clear()
    await callback.message.edit_text(
        "Хорошо! Ты можешь зарегистрироваться в другой раз, прописав <b>регистрация</b>.\n\nЧтобы узнать, что я могу, пропиши <b>помощь</b>!",
        parse_mode=ParseMode.HTML,
    )


################
##### MAIN #####
###############


async def main() -> None:
    load_dotenv()
    TOKEN = getenv("BOT_TOKEN")

    if TOKEN is None:
        print("Token not found!")
        return

    conn, cur = await db_connect()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS Chat (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    is_group BOOLEAN,
    selected_group_id VARCHAR(255) null
);"""
    )

    await db_commit_close(conn, cur)

    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    dp.include_router(router)
    await dp.start_polling(bot)
    print("polinh")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    asyncio.run(main())
