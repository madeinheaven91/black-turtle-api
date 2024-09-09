import os

import psycopg2
from psycopg2.extensions import connection, cursor


async def db_connect() -> tuple[connection, cursor]:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    cur = conn.cursor()
    return conn, cur


async def db_commit_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


async def cur_fetchone(request: str):
    conn, cur = await db_connect()
    cur.execute(request)
    res = cur.fetchone()
    await db_commit_close(conn, cur)
    return res


async def db_init() -> None:
    conn, cur = await db_connect()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS Chat (
    id BIGINT PRIMARY KEY,
    type VARCHAR(16),
    is_banned BOOLEAN DEFAULT TRUE,
    study_entity_id VARCHAR(255) NULL
);"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS TelegramUser (
    id BIGINT PRIMARY KEY,
    name VARCHAR(64),
    username VARCHAR(64),
    chat_id BIGINT,
    FOREIGN KEY (chat_id) REFERENCES Chat(id)
);"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS TelegramGroup (
    title VARCHAR(64),
    chat_id BIGINT,
    FOREIGN KEY (chat_id) REFERENCES Chat(id)
);"""
    )

    await db_commit_close(conn, cur)
