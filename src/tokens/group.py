from aiogram.types import Message
from data import groups_csv
from src.exceptions import UnknownGroupError

async def process_group_token(group_token: str):
    if group_token not in groups_csv:
        raise UnknownGroupError("Unknown group (" + group_token + ")")
    group_id = groups_csv[group_token]
    return group_id

