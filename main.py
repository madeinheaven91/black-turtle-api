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

from data import *
from src.db import db_commit_close, db_connect
from src.dispatcher import *
from src.handlers import (handle_bell, handle_exception, handle_fio,
                          handle_groups, handle_help, handle_lessons)
from src.keyboards import *
from src.state_machines import *
from src.utils import log_request, safe_message


################
##### MAIN #####
###############


async def main() -> None:
    load_dotenv()
    

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
    

    dp.include_router(router)
    await dp.start_polling(bot)
    print("polinh")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    asyncio.run(main())
