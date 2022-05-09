# import sys
# sys.path.append('../')

from services import insert
from backoff import backoff


class SqliteLoader:
    def __init__(self, sqlite_connection):
        self.sqlite_connection = sqlite_connection

    @backoff()
    def save_to_table(self, table: str, data: tuple) -> None:
        cursor = self.sqlite_connection.cursor()
        keys = tuple(data[0].__dict__.keys())
        # Очищаем её от всех данных
        cursor.execute(f"""DELETE FROM {table}""")

        for element in data:
            arguments = element.__dict__.values()
            arguments = tuple(arguments)
            cursor.execute(insert(table, keys, arguments), arguments)
        
        self.sqlite_connection.commit()
        cursor.close()
