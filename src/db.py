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
        """
    CREATE TABLE IF NOT EXISTS Chat (
    id BIGINT PRIMARY KEY UNIQUE,
    name VARCHAR(32),
    username VARCHAR(32) NULL,
    type VARCHAR(16),
    is_banned BOOLEAN DEFAULT FALSE,
    study_entity_id BIGINT NULL,
    study_entity_type VARCHAR(16) NULL
);"""
    )

    await db_commit_close(conn, cur)
