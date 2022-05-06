from time import sleep

from loguru import logger

from connections import sqlite_connector
from export import GDriveExport

def etl(connector) -> None:
    """
    Main etl process
    """
    while True:
       
       export = GDriveExport()
       registration_result = export.export_registration()
       main_result = export.export_main()
       print("registration", registration_result)
       print("main", main_result)
       sleep(10)


if __name__ == '__main__':
    logger.add("debug.log", format="{time} {level} {message}", level="INFO", rotation="1 MB")

    try:
        with sqlite_connector("../database.db") as sqlite_conn:
            etl(sqlite_conn)
    except Exception as exc:
        logger.error(f"{exc}")