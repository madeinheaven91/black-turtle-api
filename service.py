import datetime
import json
from dataclasses import dataclass

import requests
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from data import data

group_to_id = data.group_to_id
schedule_url = "https://schedule.mstimetables.ru/api/publications/group/lessons"
req_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Content-Type": "application/json",
    "Accept": "*/*",
}

    ### Токены:

    # Пары:
    # 1) "пары"
    # 2) номер группы
    # 3) "" (сегодня) / "завтра" / "неделя"
async def handle_lessons(message: Message, tokens: list[str]) -> None:
    group_query = tokens[1]
    group_id = group_to_id.get(group_query)

    if tokens[1] == "":
        await message.answer(
            "<b>Как узнать расписание пар:</b>\n\n<i>пары  (номер группы)  (сегодня, завтра)</i>\n\n<b>Например</b>: пары 921 завтра\nЕсли нужно узнать пары на сегодня, то можно написать просто 'пары 921'",
            parse_mode=ParseMode.HTML,
        )
        return

    match tokens[2].lower():
        case "" | "сегодня":
            query_date = datetime.date.today()
        case "завтра":
            query_date = datetime.date.today() + datetime.timedelta(days=1)
        case _:
            query_date = datetime.date.today()

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
        "date": str(query_date),
        "publicationId": "47eff233-d796-4b9d-8099-7abf72277af9",
    }

    response = json.loads(
        requests.post(schedule_url, json=payload, headers=req_headers).text
    )
    lessons = response.get("lessons")

    temp = []
    for lesson in lessons:
        if lesson.get("weekday") == query_date.weekday() + 1:
            temp.append(json_to_lesson(lesson))
    temp = sorted(temp, key=lambda x: x.start_time)

    lessons_today = []
    for i in range(len(temp)):
        if i == len(temp) - 1:
            lessons_today.append(temp[i])
            continue

        if temp[i].start_time == temp[i + 1].start_time:
            lessons_today.append(combine_simultaneous(temp[i], temp[i + 1]))
        elif temp[i].start_time == temp[i - 1].start_time:
            ()
        else:
            lessons_today.append(temp[i])

    res = (
        "<b>Пары "
        + response.get("group").get("name")
        + " на "
        + str(query_date.strftime("%d.%m.%Y"))
        + "</b>\n\n"
    )
    match len(lessons_today):
        case 0:
            res += "-------------------------------------------\n\n"
            res += "<b>Сегодня нет пар! 🥳🥳🥳</b>\nМожно отдыхать..."
        case _:
            for index, lesson in enumerate(lessons_today):
                res += (
                    "|------------------| "
                    + str(lesson.number)
                    + " |------------------|"
                )
                res += "\n\n"
                res += (
                    "⏳ " + lesson.start_time_str + " - " + lesson.end_time_str + "\n"
                )
                res += "📖 <b>" + lesson.name + "</b>\n"
                res += "🎓 " + lesson.teacher + "\n"
                res += "🔑 " + lesson.cabinet + "\n\n"

    await message.answer(res, parse_mode=ParseMode.HTML)


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
    number: int

    def __init__(
        self,
        name,
        teacher,
        cabinet,
        start_time,
        end_time,
        start_time_str,
        end_time_str,
        number,
    ):
        self.name = name
        self.teacher = teacher
        self.cabinet = cabinet
        self.start_time = start_time
        self.end_time = end_time
        self.start_time_str = start_time_str
        self.end_time_str = end_time_str
        self.number = number


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
    number = data.get("lesson")

    return Lesson(
        name,
        teacher,
        cabinet,
        start_time,
        end_time,
        start_time_str,
        end_time_str,
        number,
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
        number=les1.number,
    )

async def handle_fio(message: Message, tokens: list[str]) -> None:
    if tokens[1] == "":
        await message.answer("Как узнать ФИО преподавателя:\n\n<i>фио  (фамилия)</i>\n\n<b>Например:</b> фио Димитриев", parse_mode=ParseMode.HTML)
        return

    surname = tokens[1].lower().capitalize()
    name = data.teacher_names.get(surname)
    if name is None:
        await message.answer("Такого учителя нет...")
        return
    await message.answer(str(surname + " " + name))
