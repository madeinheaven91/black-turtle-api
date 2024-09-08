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
