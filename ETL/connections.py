from contextlib import contextmanager
# import psycopg2
import sqlite3


# @contextmanager
# def postgres_connector(dsn: dict):
#     conn = psycopg2.connect(**dsn)
#     yield conn
#     conn.close()

@contextmanager
def sqlite_connector(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close() 
