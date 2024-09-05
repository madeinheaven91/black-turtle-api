import asyncio
import locale
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from handlers import handle_bell, handle_errors, handle_fio, handle_groups, handle_lessons
from utils import log_request
from message_strings import help_str

dp = Dispatcher()
router = Router(name=__name__)


@router.message(F.text)
async def msg_handler(message: Message) -> None:
    ## Initialize tokens
    tokens = message.text.split(" ")
    while len(tokens) < 3:
        tokens.append("")

    match tokens[0].lower():
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
        await message.answer("Я умер")
        await dp.stop_polling()


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    log_request(message)
    await message.answer(help_str)


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    log_request(message)
    await message.answer(help_str)


async def main() -> None:
    TOKEN = getenv("BOT_TOKEN")

    if TOKEN is None:
        print("Token not found!")
        return

    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    asyncio.run(main())
