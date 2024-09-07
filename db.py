import os
import psycopg2
from psycopg2.extensions import connection, cursor


async def db_connect() -> tuple[connection, cursor]:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()
    return conn, cur


async def db_commit_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()
