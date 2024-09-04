import datetime
import json
import locale

import requests
from aiogram.types import Message

from data import data
from utils import *

async def handle_lessons(message: Message, tokens: list[str]) -> None:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    group_query = tokens[1]
    group_id = data.group_to_id.get(group_query)

    match tokens[2].lower():
        case "" | "сегодня":
            query_date = datetime.date.today()
        case "завтра":
            query_date = datetime.date.today() + datetime.timedelta(days=1)
        case "послезавтра":
            query_date = datetime.date.today() + datetime.timedelta(days=2)
        case _:
            query_date = datetime.date.today()

    ### LOGGING ###
    print(
        "\t"
            + str(datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S"))
        + " "
        + str(message.from_user.full_name)
        + " (@"
        + str(message.from_user.username)
        + ") requested "
        + str(group_query)
        + " for "
        + str(query_date.strftime("%d.%m.%y"))
    )

    if tokens[1] == "":
        await message.answer(
            "Что-то пошло не так...\nПропишите <i>/help</i> для вывода списка команд"
        )
        return
    if group_id is None:
        await message.answer("Такой группы нет")
        return

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

    lessons_today = collapse(temp)

    res = (
        "<b>"
        + response.get("group").get("name")
        + "\n"
        + str(query_date.strftime("%A, "))
        + str(len(lessons_today))
        + " "
        + lessons_declension(len(lessons_today))
        + "\n"
        + str(query_date.strftime("%d.%m.%y"))
        + "</b>\n\n"
    )
    match len(lessons_today):
        case 0:
            res += "—————————————————\n\n"
            res += "<b>Сегодня нет пар! 🥳🥳🥳</b>\nМожно отдыхать..."
        case _:
            for index, lesson in enumerate(lessons_today):
                res += "———————| " + str(lesson.number) + " урок" + " |———————"
                res += "\n\n"
                res += (
                    "⏳ " + lesson.start_time_str + " - " + lesson.end_time_str + "\n"
                )
                res += "📖 <b>" + lesson.name + "</b>\n"
                res += "🎓 " + lesson.teacher + "\n"
                res += "🔑 " + lesson.cabinet + "\n\n"

    await message.answer(res)


async def handle_fio(message: Message, tokens: list[str]) -> None:
    if tokens[1] == "":
        await message.answer(
            "Как узнать ФИО преподавателя:\n\n<i>фио  (фамилия)</i>\n\n<b>Например:</b> фио Димитриев"
        )
        return

    surname = tokens[1].lower().capitalize()
    name = data.teacher_names.get(surname)
    if name is None:
        await message.answer("Такого учителя нет...")
        return
    await message.answer(str(surname + " " + name))

    ### Токены
    #
    # 1) группы
    # 2) курсы, спец
    # 3)


async def handle_groups(message: Message, tokens: list[str]) -> None:
    if tokens[1] == "":
        await message.answer(
            "Как узнать группы:\n\n<i>группы  (название группы)</i>\n\n<b>Например:</b> группы 11-А"
        )
