import csv
from dataclasses import dataclass
from datetime import datetime

from aiogram.types import Message

help_str = """
<b>Пары:</b>    <i>пары  [номер группы]  [сегодня | завтра | день недели ]</i>
<i>Примеры:
        пары 921
        пары 921 завтра
        пары 921 вторник
        пары 921 вт</i>
Примечание:    "сегодня" писать необязательно, "пары 921" тоже будет работать

<b>Фио:</b>     <i>фио  [фамилия | имя | отчество]</i>
<i>Примеры:
        фио Димитриев
        фио александр
        фио олегович</i>
Примечание:   имена взяты с tatar.edu, поэтому информация может быть устаревшей или неправильной
        
<u>Если нашли ошибку, пишите сюда: @madeinheaven91</u>"""

schedule_url = "https://schedule.mstimetables.ru/api/publications/group/lessons"
req_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Content-Type": "application/json",
    "Accept": "*/*",
}

with open("data/groups.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    groups_csv = list(csv_reader)

with open("data/teachers.csv", "r") as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)
    teachers_csv = list(csv_reader)

groups_csv = groups_csv
teachers_csv = teachers_csv

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


def log_request(message: Message):
    print(
        f"{datetime.now().strftime('| %d.%m.%y | %H:%M:%S |')} {str(message.from_user.full_name)} ({str(message.from_user.username)}): {str(message.text)}"
    )
