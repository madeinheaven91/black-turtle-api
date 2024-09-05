import json
from datetime import date, timedelta
from logging import error

import requests
from aiogram.types import Message

from utils import *
from message_strings import *

async def handle_lessons(message: Message, tokens: list[str]) -> None:
    group_query = tokens[1].lower()
    if group_query == "":
        await message.answer(
            """⚠️ Укажите группу, пары которой надо узнать.

            <i>Пример: пары 921</i>"""
        )
        return

    try:
        group_id = [group for group in groups_csv if group[0] == group_query][0][1]
    except Exception as e:
        await message.answer("⚠️ Такой группы нет")
        return

    match tokens[2].lower():
        case "завтра":
            query_date = date.today() + timedelta(days=1)
        case "понедельник" | "пн" | "пон":
            query_date = date.today() - timedelta(days=date.today().weekday())
        case "вторник" | "вт" | "втор":
            query_date = date.today() - timedelta(days=date.today().weekday() - 1)
        case "среда" | "ср" | "сред":
            query_date = date.today() - timedelta(days=date.today().weekday() - 2)
        case "четверг" | "чт" | "чет":
            query_date = date.today() - timedelta(days=date.today().weekday() - 3)
        case "пятница" | "пт" | "пят":
            query_date = date.today() - timedelta(days=date.today().weekday() - 4)
        case "суббота" | "сб" | "суб":
            query_date = date.today() - timedelta(days=date.today().weekday() - 5)
        case "воскресенье" | "вс" | "вос" | "воск":
            await message.answer("😳 В воскресенье пар нет...")
            return
        case "" | "сегодня":
            query_date = date.today()
        case _:
            raise Exception("Unhandled 2nd token")

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
                res += "———————| " + str(lesson.index) + " урок" + " |———————"
                res += "\n\n"
                res += "⏳ " + lesson.time_str + "\n"
                res += "📖 <b>" + lesson.name + "</b>\n"
                res += "🎓 " + lesson.teacher + "\n"
                res += "🔑 " + lesson.cabinet + "\n\n"
    await message.answer(res)


async def handle_fio(message: Message, tokens: list[str]) -> None:
    teacher_query = tokens[1].lower().capitalize()
    if teacher_query == "":
        await message.answer(
            "Как узнать ФИО преподавателя:\n\n<i>фио  (фамилия)</i>\n\n<b>Например:</b> фио Димитриев"
        )
        return

    teachers = [
        teacher
        for teacher in teachers_csv
        if teacher[0] == teacher_query
        or teacher[1] == teacher_query
        or teacher[2] == teacher_query
    ]
    if teachers == []:
        await message.answer("⚠️ Такого преподавателя нет...")
        return

    res = "👨‍🏫 Найдены учителя:\n"
    for teacher in teachers:
        res += f"   {teacher[0]} {teacher[1]} {teacher[2]}\n"

    await message.answer(res)


async def handle_bell(message: Message, tokens: list[str]) -> None:
    type_query = tokens[1].lower()
    match type_query:
        case "":
            if datetime.today().weekday() == 5:
                is_saturday = True
            else:
                is_saturday = False
        case "суббота" | "сб":
            is_saturday = True
        case "будни":
            is_saturday = False
        case _:
            await message.answer("⚠️ Неправильно введена команда")
            return

    if is_saturday == False:
        await message.answer(bell_regular_str)
    else:
        await message.answer(bell_saturday_str)


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


async def handle_errors(handler, message: Message, tokens: list[str]) -> None:
    try:
        await handler(message, tokens)
    except Exception as e:
        error(e)
        await message.answer(
            "🚫 Что-то пошло не так...\nПропишите <i>/help</i> для вывода списка команд"
        )
