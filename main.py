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
from src.db import db_commit_close, db_connect, db_init
from src.dispatcher import *
from src.handlers import (
    handle_bell,
    handle_exception,
    handle_fio,
    handle_groups,
    handle_help,
    handle_lessons,
)
from src.keyboards import *
from src.state_machines import *
from src.utils import log_request, safe_message

################
##### MAIN #####
###############


async def main() -> None:
    load_dotenv()
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

    conn, cur = await db_connect()
    await db_init()
    await db_commit_close(conn, cur)

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    asyncio.run(main())
