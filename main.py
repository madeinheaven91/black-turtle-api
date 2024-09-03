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
from data import dic

######################
### Some variables ###
######################
TOKEN = getenv("BOT_TOKEN")
group_to_id = dic.group_to_id
schedule_url = "https://schedule.mstimetables.ru/api/publications/group/lessons"
req_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Content-Type": "application/json",
    "Accept": "*/*",
}

#############
### Utils ###
#############
@dataclass
class Lesson:
    name: str
    teacher: str
    cabinet: str
    start_time: int
    end_time: int
    start_time_str: str
    end_time_str: str

    def __init__(
        self, name, teacher, cabinet, start_time, end_time, start_time_str, end_time_str
    ):
        self.name = name
        self.teacher = teacher
        self.cabinet = cabinet
        self.start_time = start_time
        self.end_time = end_time
        self.start_time_str = start_time_str
        self.end_time_str = end_time_str

def json_to_lesson(data) -> Lesson:
    if data.get("subject").get("name") is None:
        name = "<i>Предмет не указан</i>"
    else:
        name = data.get("subject").get("name")

    if data.get("teachers")[0].get("fio") is None:
        teacher = "<i>Учитель не указан</i>"
    else:
        teacher = data.get("teachers")[0].get("fio")

    if data.get("cabinet") is None:
        cabinet = "<i>Кабинет не указан</i>"
    else:
        cabinet = data.get("cabinet").get("name")

    start_time = data.get("startTimeMin")
    end_time = data.get("endTimeMin")
    start_time_str = data.get("startTime")
    end_time_str = data.get("endTime")

    return Lesson(
        name,
        teacher,
        cabinet,
        start_time,
        end_time,
        start_time_str,
        end_time_str,
    )

def combine_simultaneous(les1: Lesson, les2: Lesson) -> Lesson:
    return Lesson(
        name=les1.name,
        teacher=les1.teacher + " / " + les2.teacher,
        cabinet=les1.cabinet + " / " + les2.cabinet,
        start_time=les1.start_time,
        end_time=les1.end_time,
        start_time_str=les1.start_time_str,
        end_time_str=les1.end_time_str,
    )
###########
### Bot ###
###########

dp = Dispatcher()

@dp.message()
async def echo_handler(message: Message) -> None:
    if message.text.lower().split(" ")[0] == "пары":
        group_query = message.text.split(" ")[1]
        group_id = group_to_id.get(group_query)
        today = datetime.date.today()

        if group_id is None:
            await message.answer("Такой группы нет")
            return
        else:
            print(
                "\t\t"
                + str(message.from_user.full_name)
                + " (@"
                + str(message.from_user.username)
                + ") requested "
                + str(group_query)
                + " (id: "
                + str(group_id)
                + ")"
            )

        payload = {
            "groupId": group_id,
            "date": str(today.today()),
            "publicationId": "47eff233-d796-4b9d-8099-7abf72277af9",
        }

        response = json.loads(
            requests.post(schedule_url, json=payload, headers=req_headers).text
        )
        lessons = response.get("lessons")

        temp = []
        for lesson in lessons:
            if lesson.get("weekday") == today.weekday() + 1:
                temp.append(json_to_lesson(lesson))
        temp = sorted(temp, key=lambda x: x.start_time)

        lessons_today = []
        for i in range(len(temp)):
            if i != len(temp) - 1:
                if temp[i].start_time == temp[i + 1].start_time:
                    lessons_today.append(
                        combine_simultaneous(temp[i], temp[i + 1])
                    )
                elif (
                    temp[i].start_time == temp[i - 1].start_time
                ):  # FIXME: something bad
                    ()
                else:
                    lessons_today.append(temp[i])
            else:
                lessons_today.append(temp[i])

        res = (
            "<b>Пары "
            + response.get("group").get("name")
            + " на "
            + str(today.today())
            + "</b>\n\n"
        )
        match len(lessons_today):
            case 0:
                res += "-------------------------------------------\n\n"
                res += "<b>Сегодня нет пар! 🥳🥳🥳</b>\nМожно отдыхать..."
            case _:
                for lesson in lessons_today:
                    res += "-------------------------------------------\n\n"
                    res += (
                        "⏳ "
                        + lesson.start_time_str
                        + " - "
                        + lesson.end_time_str
                        + "\n"
                    )
                    res += "📖 <b>" + lesson.name + "</b>\n"
                    res += "🎓 " + lesson.teacher + "\n"
                    res += "🔑 " + lesson.cabinet + "\n\n"

        await message.answer(res, parse_mode=ParseMode.HTML)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
