from datetime import date, timedelta

from src.exceptions import WeekError


# Takes modifer and date tokens and returns date
def process_week_token(token: str, query_date: date, ignore_week: bool = False) -> date:
    if ignore_week: return query_date
    match token:
        case "":
            if (date.today().weekday() > query_date.weekday()):
                query_date += timedelta(days=7)
            else:
                query_date = query_date
        case "этот" | "эта":
            query_date = query_date
        case "след" | "следующий" | "следующая":
            query_date += timedelta(days=7)
        case "прош" | "пр" | "прошлый" | "прошлая":
            query_date -= timedelta(days=7)
        case _:
            raise WeekError("Couldn't process week token (" + token + ")")
    return query_date
