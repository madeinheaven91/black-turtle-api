import asyncio
import datetime
import json
import logging
import sys
import threading
from dataclasses import dataclass
from os import getenv

import requests
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from data import data
from service import handle_fio, handle_lessons

dp = Dispatcher()

@dp.message()
async def echo_handler(message: Message) -> None:
    ## Initialize tokens
    tokens = message.text.split(" ")
    while len(tokens) < 3:
        tokens.append("")

    match tokens[0].lower():
        case "пары":
           await handle_lessons(message, tokens) 
        case "фио":
            await handle_fio(message, tokens)
        case _:
            await message.answer("Не понимаю тебя...\n\nНа данный момент можно узнать <b>пары</b> и <b>фио</b>", parse_mode=ParseMode.HTML)

async def main() -> None:
    TOKEN = getenv("BOT_TOKEN")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
