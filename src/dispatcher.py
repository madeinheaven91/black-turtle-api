import logging
import re
from os import getenv

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dotenv import load_dotenv

from data import *
from src.db import db_commit_close, db_connect
from src.dispatcher import *
from src.exceptions import UnknownGroupError
from src.handlers import (handle_bell, handle_exception, handle_fio,
                          handle_groups, handle_help, handle_lessons)
from src.keyboards import *
from src.state_machines import *
from src.tokens.group import process_group_token
from src.tokens.teacher import process_teacher_token
from src.utils import log_request, safe_message

dp = Dispatcher()
router= Router(name=__name__)

ignored_chats: set[str] = {""};

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

if TOKEN is None:
    print("Token not found!")


bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)

################
###          ###
### COMMANDS ###
###          ###
################


@router.message(F.text)
async def msg_handler(message: Message) -> None:
    if message.chat.id in ignored_chats:
        return
    ## Initialize tokens
    tokens = re.sub(" +", " ", message.text.lower().strip()).split(" ")
    while len(tokens) < 5:
        tokens.append("")

    match tokens[0]:
        case "помощь":
            await log_request(message)
            await handle_exception(handle_help, message, tokens)
        case "пары":
            await log_request(message)
            await handle_exception(handle_lessons, message, tokens)
        case "фио":
            await log_request(message)
            await handle_exception(handle_fio, message, tokens)
        case "звонки":
            await log_request(message)
            await handle_exception(handle_bell, message, tokens)
        case "группы":
            await log_request(message)
            await handle_exception(handle_groups, message, tokens)


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await log_request(message)
    ignored_chats.add(message.chat.id)

    # Database stuff
    conn, cur = await db_connect()
    cur.execute("""SELECT id from Chat WHERE id=%s""", (message.chat.id,))
    exists = cur.fetchone()

    if exists is None:
        chat_id = message.chat.id
        chat_type = message.chat.type

        name = message.chat.title
        if chat_type == "private":
            username = message.from_user.username
            cur.execute(
                """
                    INSERT INTO Chat (id, name, username, type)
                    VALUES (%s, %s, %s, %s) 
                    ON CONFLICT (id) DO NOTHING
                    """,
                (chat_id, name, username, chat_type)
            )
        else:
            cur.execute(
                """
                    INSERT INTO Chat (id, name, type)
                    VALUES (%s, %s, %s) 
                    """,
                (chat_id, name, chat_type)
            )
    await db_commit_close(conn, cur)

    try:
        await message.answer(
            "✋ Привет! Для начала давайте выберем группу, в которой вы учитесь.",
            reply_markup=greeting_kb,
        )
    except Exception as e:
        logging.error(e)


@dp.callback_query(F.data == "reg_yes")
async def reg_yes(callback: CallbackQuery) -> None:
    await callback.message.edit_text("❔ Вы хотите узнавать пары <b>группы</b> или <b>преподавателя</b>?", parse_mode=ParseMode.HTML, reply_markup=reg_group_or_teacher_kb)
    await callback.answer()

@dp.callback_query(F.data == "reg_group")
async def reg_choose_group_callback(callback: CallbackQuery, state: FSMContext) -> None:
    if ignored_chats.__contains__(callback.message.chat.id): ignored_chats.remove(callback.message.chat.id)
    await callback.message.edit_text("❔ Введите номер группы", parse_mode=ParseMode.HTML)
    await state.set_state(Registration.select_group)
    await callback.answer()

@dp.callback_query(F.data == "reg_teacher")
async def reg_choose_teacher_callback(callback: CallbackQuery, state: FSMContext) -> None:
    if ignored_chats.__contains__(callback.message.chat.id): ignored_chats.remove(callback.message.chat.id)
    await callback.message.edit_text("❔ Введите фамилию преподавателя", parse_mode=ParseMode.HTML)
    await state.set_state(Registration.select_teacher)
    await callback.answer()


@dp.callback_query(F.data == "reg_no")
async def reg_no(callback: CallbackQuery) -> None:
    if ignored_chats.__contains__(callback.message.chat.id): ignored_chats.remove(callback.message.chat.id)
    await callback.message.edit_text(
        "ℹ️ Хорошо! Вы можете зарегистрироваться в другой раз, прописав <b>регистрация</b>.\n\nЧтобы узнать, что я могу, пропишите <b>помощь</b>!",
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@dp.message(Registration.select_group)
async def select_group(message: Message, state: FSMContext) -> None:
    await log_request(message)
    try:
        group_id = process_group_token(message.text)[0]
    except Exception:
        await state.set_state(Registration.select_group)
        await message.answer(
            """⚠️ <b>Такой группы нет...</b>

Отправьте номер своей группы еще раз.""",
            reply_markup=reg_end_kb,
        )
        logging.error("Unknown group (" + message.text + ")");
        return;

    conn, cur = await db_connect()
    cur.execute(
        """UPDATE Chat
    SET study_entity_id=%s, study_entity_type=%s
    WHERE id=%s""",
        (group_id,"group",message.chat.id),
    )
    await db_commit_close(conn, cur)

    try:
        await message.answer(
            """✅ Отлично, группа выбрана! Теперь вы можете смотреть пары своей группы!\n\nЧтобы узнать, что я могу, пропишите <b>помощь</b>!""",
            parse_mode=ParseMode.HTML,
            reply_markup=default_kb,
        )
    except Exception as e:
        logging.error(e)

    await state.clear()

@dp.message(Registration.select_teacher)
async def select_teacher(message: Message, state: FSMContext) -> None:
    await log_request(message)
    try:
        teachers = process_teacher_token(message.text)
        if len(teachers) == 1:
            teacher_id = teachers[0][0]
        else:
            await message.answer("Найдено много преподов...")
            return;
    except Exception:
        await state.set_state(Registration.select_teacher)
        await message.answer(
            """⚠️ <b>Такого преподавателя нет...</b>

Отправьте фамилию еще раз.""",
            reply_markup=reg_end_kb,
        )
        logging.error("Unknown teacher (" + message.text + ")");
        return;

    conn, cur = await db_connect()
    cur.execute(
        """UPDATE Chat
    SET study_entity_id=%s, study_entity_type=%s
    WHERE id=%s""",
        (teacher_id,"teacher",message.chat.id),
    )
    await db_commit_close(conn, cur)

    try:
        await message.answer(
            """✅ Отлично, преподаватель выбран! Теперь вы можете смотреть его пары!\n\nЧтобы узнать, что я могу, пропишите <b>помощь</b>!""",
            parse_mode=ParseMode.HTML,
            reply_markup=default_kb,
        )
    except Exception as e:
        logging.error(e)

    await state.clear()


@dp.message(F.text.lower() == "регистрация")
async def registration(message: Message) -> None:
    await log_request(message)
    await message.answer("❔ Вы хотите узнавать пары <b>группы</b> или <b>преподавателя</b>?", parse_mode=ParseMode.HTML, reply_markup=reg_group_or_teacher_kb)

    conn, cur = await db_connect()
    cur.execute("""SELECT id from Chat WHERE id=%s""", (message.chat.id,))
    exists = cur.fetchone()

    if exists is None:
        chat_id = message.chat.id
        chat_type = message.chat.type
        name = message.chat.title
        if chat_type == "private":
            username = message.from_user.username
            cur.execute(
                """
                    INSERT INTO Chat (id, type, name, username)
                    VALUES (%s, %s, %s, %s) 
                    ON CONFLICT (id) DO NOTHING
                    """,
                (chat_id, chat_type, name, username)
            )
        else:
            cur.execute(
                """
                    INSERT INTO Chat (id, type, name)
                    VALUES (%s, %s, %s) 
                    """,
                (chat_id, chat_type, name)
            )
    await db_commit_close(conn, cur)


@dp.callback_query(F.data == "reg_end")
async def process_callback_exit(callback: CallbackQuery, state: FSMContext) -> None:
    if ignored_chats.__contains__(callback.message.chat.id): ignored_chats.remove(callback.message.chat.id)
    await state.clear()
    await callback.message.edit_text(
        "ℹ️ Хорошо! Вы можете зарегистрироваться в другой раз, прописав <b>регистрация</b>.\n\nЧтобы узнать, что я могу, пропишите <b>помощь</b>!",
        parse_mode=ParseMode.HTML,
    )


######################
###                ###
### ADMIN COMMANDS ###
###                ###
######################


@dp.message(Command("kill"))
async def cmd_kill(message: Message) -> None:
    await log_request(message)
    if message.from_user.id == 2087648271:
        await safe_message(message, "Я умер")
        await dp.stop_polling()


@dp.message(Command("send"))
async def cmd_send(message: Message) -> None:
    await log_request(message)
    if message.from_user.id == 2087648271:
        text = message.text
        while len(text.split(" ")) < 3:
            text += " ."

        if text.split(" ")[2] == ".":
            await message.reply("Сообщение пусто!")
            return
        address_id = text.split(" ")[1]
        msg = text.split(" ", 2)[2]
        try:
            await bot.send_message(address_id, msg, parse_mode=ParseMode.HTML)
            await message.reply("Отправлено")
        except Exception as e:
            await message.reply("Не получилось отправить")
    else:
        ()


@dp.message(Command("send_all"))
async def cmd_send_all(message: Message) -> None:
    await log_request(message)
    if message.from_user.id == 2087648271:
        text = message.text
        while len(text.split(" ")) < 2:
            text += " ."
        msg = text.split(" ", 1)[1]

        if msg == ".":
            await message.reply("Сообщение пусто!")
            return
        conn, cur = await db_connect()
        cur.execute("SELECT id FROM Chat")
        chats = cur.fetchall()
        ids = []
        for chat in chats:
            ids.append(chat[0])

        await db_commit_close(conn, cur)

        successful = 0
        failed = 0
        for id in ids:
            try:
                await bot.send_message(id, msg, parse_mode=ParseMode.HTML)
                successful += 1
            except:
                failed += 1

        await message.reply(
            "Отправлено (всего: "
            + str(len(ids))
            + ", успешно: "
            + str(successful)
            + ", неудачно: "
            + str(failed)
            + ")"
        )
        # try:
        #     await bot.send_message(address_id, msg, parse_mode=ParseMode.HTML)
        #     await message.reply("Отправлено")
        # except Exception as e:
        #     await message.reply("Не получилось отправить")
    else:
        ()
