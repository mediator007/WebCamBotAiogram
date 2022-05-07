# import sys
# sys.path.append('../')

from loguru import logger 

from services import insert, table_creation
from backoff import backoff


class SqliteLoader:
    def __init__(self, sqlite_connection):
        self.sqlite_connection = sqlite_connection

    @backoff()
    def save_to_table(self, table: str, conflict_field: str,  data: tuple) -> None:
        cursor = self.sqlite_connection.cursor()
        keys = data[0].keys()
        # Создаем таблицу если её нет
        cursor.execute(table_creation(table, keys))
        # Очищаем её от всех данных
        cursor.execute(f"""DELETE FROM {table}""")

        for element in data:
            arguments = element.values()
            arguments = tuple(arguments)
            cursor.execute(insert(table, keys, arguments, conflict_field), arguments)

        self.sqlite_connection.commit()
        cursor.close()
