from aiogram.types import Message
from data import groups_csv
from src.exceptions import UnknownGroupError

def process_group_token(group_token: str):
    try:
        result = [sublist for sublist in groups_csv if sublist[1] == group_token][0]
        return result;
    except IndexError:
        raise UnknownGroupError("Unknown group (" + group_token + ")")

