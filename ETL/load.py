# import sys
# sys.path.append('../')

from loguru import logger 

from services import insert
from backoff import backoff


class SqliteLoader:
    def __init__(self, sqlite_connection):
        self.sqlite_connection = sqlite_connection

    @backoff()
    def save_to_table(self, table:str, conflict_field:str,  data: tuple) -> None:
        cursor = self.sqlite_connection.cursor()
        
        for element in data:
            arguments = []
            keys = []
            for key, value in element.items():
                keys.append(key)
                arguments = list(arguments)
                arguments.append(value)
                arguments = tuple(arguments)
                cursor.execute(insert(table, keys, arguments, conflict_field))

        cursor.close()
