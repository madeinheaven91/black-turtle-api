import json
from datetime import date, timedelta
from logging import error

import requests
from aiogram.types import Message

from db import db_connect
from message_strings import *
from utils import *


# TOKENS
#
# (0) пары
# (1) "", "завтра", день недели / group_query
# (2) "", "завтра", день недели
#
async def handle_lessons(message: Message, tokens: list[str]) -> None:
    token_fst = tokens[1]
    token_snd = tokens[2]
    token_trd = tokens[3]

    if token_fst not in groups_csv:
        date_query = token_fst
        date_modifier_query = token_snd
        conn, cur = await db_connect()

        cur.execute(
            """SELECT chat.selected_group_id FROM Chat where id=%s""",
            (message.chat.id,),
        )
        group_id = cur.fetchone()[0]

        if group_id is None:
            await safe_message(
                message,
                "Я не знаю, в какой ты группе! Пропиши /start, чтобы выбрать свою группу",
            )
            return

        match date_query:
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
                raise Exception("Unhandled token")

        match date_modifier_query:
            case "след" | "следующий" | "следующая":
                query_date += timedelta(days=7)
            case "прош" | "пр" | "прошлый" | "прошлая":
                query_date -= timedelta(days=7)

        payload = {
            "groupId": group_id,
            "date": str(query_date),
            "publicationId": "47eff233-d796-4b9d-8099-7abf72277af9",
        }

        response = json.loads(
            requests.post(schedule_url, json=payload, headers=req_headers).text
        )

        msg = lessons_string(response, query_date)
        await safe_message(message, msg)
        return
    else:
        group_query = token_fst
        date_query = token_snd
        date_modifier_query = token_trd

        if group_query not in groups_csv:
            await safe_message(message, "⚠️ Такой группы нет")
            return
        else:
            group_id = groups_csv[group_query]

        match date_query:
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

        match date_modifier_query:
            case "след" | "следующий" | "следующая":
                query_date += timedelta(days=7)
            case "прош" | "пр" | "прошлый" | "прошлая":
                query_date -= timedelta(days=7)

        payload = {
            "groupId": group_id,
            "date": str(query_date),
            "publicationId": "47eff233-d796-4b9d-8099-7abf72277af9",
        }

        response = json.loads(
            requests.post(schedule_url, json=payload, headers=req_headers).text
        )

        msg = lessons_string(response, query_date)
        await safe_message(message, msg)


async def handle_fio(message: Message, tokens: list[str]) -> None:
    teacher_query = tokens[1].capitalize()
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
        await message.answer(
            "⚠️ <b>Такого преподавателя нет...</b>\n\n<i>Если нужный учитель не был найден, пишите @madeinheaven91</i>"
        )
        return

    res = "👨‍🏫 <b>Найдены учителя</b>:\n"
    for teacher in teachers:
        res += f"   {teacher[0]} {teacher[1]} {teacher[2]}\n"
    res += "\n<i>Если нужный учитель не был найден, пишите @madeinheaven91</i>"
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
