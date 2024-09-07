import asyncio
import locale
import logging
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

from db import db_commit_close, db_connect
from handlers import (
    handle_bell,
    handle_errors,
    handle_fio,
    handle_groups,
    handle_lessons,
)
from message_strings import help_str
from utils import *
from utils import log_request

dp = Dispatcher()
router = Router(name=__name__)


@router.message(F.text)
async def msg_handler(message: Message) -> None:
    ## Initialize tokens
    tokens = message.text.split(" ")
    while len(tokens) < 5:
        tokens.append("")
    tokens = list(map(lambda x: x.lower(), tokens))

    match tokens[0]:
        case "пары":
            log_request(message)
            await handle_errors(handle_lessons, message, tokens)
        case "фио":
            log_request(message)
            await handle_errors(handle_fio, message, tokens)
        case "звонки":
            log_request(message)
            await handle_errors(handle_bell, message, tokens)
        case "группы":
            log_request(message)
            await handle_errors(handle_groups, message, tokens)


@dp.message(Command("kill"))
async def cmd_kill(message: Message) -> None:
    log_request(message)
    if message.from_user.id == 2087648271:
        await safe_message(message, "Я умер")
        await dp.stop_polling()


class SelectGroup(StatesGroup):
    group = State()


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    log_request(message)

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
    await state.set_state(SelectGroup.group)
    await safe_message(message, "Привет! Из какой ты группы?")


@dp.message(SelectGroup.group)
async def process_group(message: Message, state: FSMContext) -> None:
    log_request(message)
    await state.update_data(group=message.text)

    try:
        group_id = groups_csv[message.text]
    except Exception:
        await state.clear()
        await safe_message(
            message,
            "Такой группы нет...\n\nЧтобы попробовать заново, напиши /start еще раз.\nВ любом случае, пропиши /help, чтобы узнать список комманд",
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
    await safe_message(
        message,
        """Понял! Чтобы узнать пары своей группы на сегодня, пропишите "пары".""",
    )
    await state.clear()


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    log_request(message)
    await safe_message(message, help_str)


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
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    asyncio.run(main())
