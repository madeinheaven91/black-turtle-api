#############
### Utils ###
#############
from dataclasses import dataclass


@dataclass()
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


def lessons_declension(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "урок"
    elif 2 <= (count % 10) <= 4 and not 12 <= count <= 14:
        return "урока"
    else:
        return "уроков"

schedule_url = "https://schedule.mstimetables.ru/api/publications/group/lessons"
req_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    "Content-Type": "application/json",
    "Accept": "*/*",
}

