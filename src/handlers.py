import json
from logging import error

import requests
from aiogram.types import Message

from data import groups_csv
from src.db import db_commit_close, db_connect
from src.exceptions import (
    BellTypeError,
    DayError,
    GroupNotSelectedError,
    UnknownTeacherError,
    WeekError,
)
from src.message_strings import *
from src.tokens.day import process_date_token
from src.tokens.group import process_group_token
from src.tokens.teacher import process_teacher_token
from src.tokens.week import process_week_token
from src.utils import *

# TOKENS
#
# (0) пары
# (1) группа / день
# (2) день / неделя
# (3) неделя / ""


#
async def handle_lessons(message: Message, tokens: list[str]) -> None:
    # Token identification
    if tokens[1] not in groups_csv:
        day_token = tokens[1]
        week_token = tokens[2]
    else:
        group_token = tokens[1]
        day_token = tokens[2]
        week_token = tokens[3]

    if tokens[1] != day_token:  ### If the first token is group number
        group_id = await process_group_token(group_token)
        day_processed = process_date_token(day_token)
        query_date = process_week_token(
            week_token, day_processed[0], day_processed[1]
        )


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
    else:  ### If the first token is not group number
        try:
            day_processed = process_date_token(day_token)
            query_date = process_week_token(
                week_token, day_processed[0], day_processed[1]
            )
        except:
            raise UnknownGroupError("Unknown group (" + day_token + ")")

        conn, cur = await db_connect()
        cur.execute(
            """SELECT chat.selected_group_id FROM Chat where id=%s""",
            (message.chat.id,),
        )

        fetch = cur.fetchone()
        if fetch is None:
            raise GroupNotSelectedError(
                "Group not selected in chat (" + message.chat.id + ")"
            )
        group_id = fetch[0]
        await db_commit_close(conn, cur)

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


# Тoкены
# (0) фио
# (1) фамилия / имя / отчество
async def handle_fio(message: Message, tokens: list[str]) -> None:
    teacher_token = tokens[1].capitalize()

    if teacher_token == "":
        await safe_message(message, teacher_help)
        return

    teachers = process_teacher_token(teacher_token)

    res = "👨‍🏫 <b>Найдены преподаватели</b>:\n"
    for teacher in teachers:
        res += f" - {teacher[0]} {teacher[1]} {teacher[2]}\n"
    res += "\n<i>Если в базе не хватает преподавателя, пишите @madeinheaven91</i>"
    await safe_message(message, res)


# Токены
#
# (0) звонки
# (1) токен типа / ""


async def handle_bell(message: Message, tokens: list[str]) -> None:
    type_token = tokens[1]
    match type_token:
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
            raise BellTypeError("Unknown bell type")

    if is_saturday == False:
        await safe_message(message, bell_regular_msg)
    else:
        await safe_message(message, bell_saturday_msg)


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


async def handle_exception(handler, message: Message, tokens: list[str]) -> None:
    try:
        await handler(message, tokens)
    except Exception as e:
        add_prefix = True
        match e:
            case s if isinstance(e, UnknownGroupError):
                msg = "<b>Группа не найдена</b>"
            case s if isinstance(e, DayError):
                msg = "<b>Не понимаю, на какой день вы хотите получить расписание</b>"
            case s if isinstance(e, WeekError):
                msg = "<b>Не понимаю, на какую неделю вы хотите получить расписание</b>"
            case s if isinstance(e, UnknownTeacherError):
                msg = "<b>Преподаватели не найдены...</b>\n\n<i>Если в базе не хватает преподавателя, пишите @madeinheaven91</i>"
            case s if isinstance(e, BellTypeError):
                msg = "<b>Не понимаю, какие звонки вам нужны.</b>"
            case s if isinstance(e, GroupNotSelectedError):
                msg = "Я не знаю, в какой ты группе! Пропиши /start, чтобы выбрать свою группу"
            case _:
                msg = exception_msg
                add_prefix = False
        error(e)
        if add_prefix != False:
            msg = "⚠️ " + msg
        await safe_message(message, msg)
