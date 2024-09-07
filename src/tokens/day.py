from datetime import date, timedelta

from src.exceptions import DayError


# Takes date token
# returns the date and if the week token should be ignored
def process_date_token(token: str) -> tuple[date, bool]:
    ignore_week = False
    match token:
        case "" | "сегодня":
            query_date = date.today()
            ignore_week = True
        case "завтра":
            query_date = date.today() + timedelta(days=1)
            ignore_week = True
        case "вчера":
            query_date = date.today() - timedelta(days=1)
            ignore_week = True
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
            query_date = date.today() - timedelta(days=date.today().weekday() - 6)
        case _:
            raise DayError("Couldn't process day token (" + token + ")")

    return query_date, ignore_week
