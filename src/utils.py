import csv
from dataclasses import dataclass
from datetime import datetime

from aiogram.types import Message

from src.db import db_commit_close, db_connect
from src.exceptions import UnknownGroupError

schedule_url = "https://schedule.mstimetables.ru/api/publications/group/lessons"
req_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Content-Type": "application/json",
    "Accept": "*/*",
}


@dataclass()
class Lesson:
    name: str
    teacher: str
    cabinet: str
    start_time: int
    end_time: int
    time_str: str
    index: int

    def __init__(
        self,
        name,
        teacher,
        cabinet,
        start_time,
        end_time,
        time_str,
        index,
    ):
        self.name = name
        self.teacher = teacher
        self.cabinet = cabinet
        self.start_time = start_time
        self.end_time = end_time
        self.time_str = time_str
        self.index = index


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
    time_str = str(data.get("startTime")) + " — " + str(data.get("endTime"))
    index = data.get("lesson")

    return Lesson(
        name,
        teacher,
        cabinet,
        start_time,
        end_time,
        time_str,
        index,
    )


def combine_simultaneous(les1: Lesson, les2: Lesson) -> Lesson:
    return Lesson(
        name=les1.name,
        teacher=les1.teacher + " / " + les2.teacher,
        cabinet=les1.cabinet + " / " + les2.cabinet,
        start_time=les1.start_time,
        end_time=les1.end_time,
        time_str=les1.time_str,
        index=les1.index,
    )


def lessons_declension(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "урок"
    elif 2 <= (count % 10) <= 4 and not 12 <= count <= 14:
        return "урока"
    else:
        return "уроков"


def collapse(lessons: list[Lesson]) -> list[Lesson]:
    res = []
    for i in range(len(lessons) - 1):
        if lessons[i].start_time == lessons[i + 1].start_time:
            res.append(combine_simultaneous(lessons[i], lessons[i + 1]))
        elif lessons[i].start_time == lessons[i - 1].start_time:
            continue
        else:
            res.append(lessons[i])
    res.append(lessons[len(lessons) - 1])
    return res


def lessons_string(response, query_date: datetime.date):
    lessons = response.get("lessons")
    if lessons is None:
        res = (
            "<b>"
            + response.get("group").get("name")
            + "\n"
            + str(query_date.strftime("%A"))
            + "\n"
            + str(query_date.strftime("%d.%m.%y"))
            + "</b>\n\n"
            + "————| Нет расписания |————\n\n"
            + "<b>На этот день распиания пока нет...</b>"
        )
        return res

    temp = []
    for lesson in lessons:
        if lesson.get("weekday") == query_date.weekday() + 1:
            temp.append(json_to_lesson(lesson))

    if len(temp) == 0:
        res = (
            "<b>"
            + response.get("group").get("name")
            + "\n"
            + str(query_date.strftime("%A"))
            + "\n"
            + str(query_date.strftime("%d.%m.%y"))
            + "</b>\n\n"
            + "———| Нет расписания |———\n\n"
            + "<b>На этот день распиания пока нет...</b>"
        )
        return res
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
    for lesson in lessons_today:
        res += "——————| " + str(lesson.index) + " урок" + " |——————\n\n"
        res += "⏳ " + lesson.time_str + "\n"
        res += "📖 <b>" + lesson.name + "</b>\n"
        res += "🎓 " + lesson.teacher + "\n"
        res += "🔑 " + lesson.cabinet + "\n\n"

    return res


async def log_request(message: Message):
    is_group = message.chat.type != "private"
    name = message.chat.title if is_group else message.from_user.full_name

    if is_group:
        print(
            f"{datetime.now().strftime('| %d.%m.%y | %H:%M:%S |')} {name} ({str(message.from_user.username)}): {str(message.text)}"
        )
    else:
        print(
            f"{datetime.now().strftime('| %d.%m.%y | %H:%M:%S |')} {name} ({str(message.from_user.username)}): {str(message.text)}"
        )

    conn, cur = await db_connect()

    if is_group:
        cur.execute(
            """
                    UPDATE TelegramGroup 
                    SET title=%s
                    WHERE chat_id=%s
                    """,
            (name,message.chat.id),
        )
    else:
        cur.execute(
            """
                    UPDATE TelegramUser 
                    SET name=%s
                    WHERE id=%s
                    """,
            (name,message.from_user.id),
        )



    await db_commit_close(conn, cur)


async def safe_message(message: Message, msg: str) -> None:
    try:
        await message.answer(msg)
    except Exception as e:
        print(e)


def gen_payload(group_id: str, query_date: datetime.date):
    return {
        "groupId": group_id,
        "date": str(query_date),
        "publicationId": "45fc8ddd-35e2-4d8e-9da1-a081a8edc11d",
    }
