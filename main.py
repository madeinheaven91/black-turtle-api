import asyncio
from datetime import datetime
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from handlers import handle_fio, handle_groups, handle_lessons
from utils import log_request

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
            await handle_lessons(message, tokens)
        case "фио":
            log_request(message) 
            await handle_fio(message, tokens)
        case "группы":
            log_request(message) 
            await handle_groups(message, tokens)


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    log_request(message) 
    await message.answer(
        """   Привет! Я помогу тебе узнать все о расписаниях, группах и преподавателях

На данный момент можно узнать <b>пары</b> и <b>фио</b>

<b>Пары:</b>    <i>пары  [номер группы]  [сегодня | завтра | день недели ]</i>
Пример:    пары 921 сегодня
Примечание:    "сегодня" писать необязательно, "пары 921" тоже будет работать

<b>Фио:</b>     <i>фио  [фамилия]</i>
Пример:   фио Димитриев
Примечание:   имена взяты с сайта tatar.edu, поэтому информация может быть устаревшей или неправильной
        
<i>Если нашли ошибку, пишите сюда: @madeinheaven91</i>"""
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    log_request(message) 
    await message.answer(
        """<b>Пары:</b>    <i>пары  [номер группы]  [сегодня | завтра | день недели ]</i>
Пример:    пары 921 сегодня
Примечание:    "сегодня" писать необязательно, "пары 921" тоже будет работать

<b>Фио:</b>     <i>фио  [фамилия]</i>
Пример:   фио Димитриев
Примечание:   имена взяты с сайта tatar.edu, поэтому информация может быть устаревшей или неправильной
        
<i>Если нашли ошибку, пишите сюда: @madeinheaven91</i>"""
    )


async def main() -> None:
    TOKEN = getenv("BOT_TOKEN")

    if TOKEN is None:
        print("Token not found!")
        return

    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    asyncio.run(main())
