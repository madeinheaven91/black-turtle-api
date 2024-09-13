from data import teachers_csv
from src.exceptions import UnknownTeacherError

def process_teacher_token(token: str):
    token = token.lower().capitalize()
    teachers = [
        teacher
        for teacher in teachers_csv
        if teacher[1] == token
        or teacher[2] == token
        or teacher[3] == token
    ]

    if teachers == []:
        raise UnknownTeacherError("Couldn't find teacher")

    return teachers
