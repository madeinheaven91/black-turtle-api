from data import teachers_csv
from src.exceptions import UnknownTeacherError

def process_teacher_token(token: str):
    teachers = [
        teacher
        for teacher in teachers_csv
        if teacher[0] == token
        or teacher[1] == token
        or teacher[2] == token
    ]

    if teachers == []:
        raise UnknownTeacherError("Couldn't find teacher")

    return teachers
