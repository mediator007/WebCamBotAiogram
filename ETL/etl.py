from time import sleep

from loguru import logger

from connections import sqlite_connector
from export import GDriveExport
from transform import main_transform, registration_transform
from load import SqliteLoader
from db_manage import create_main, create_registration


def etl(connector) -> None:
    """
    Main etl process
    """
    while True:
        # Export
        export = GDriveExport()
        registration_result = export.export_registration()
        main_result = export.export_main()

        # Transform
        transform_registration_res = registration_transform(registration_result)
        transform_main_res = main_transform(main_result)

        # Load
        loader = SqliteLoader(connector)
        loader.save_to_table('registration', transform_registration_res)
        loader.save_to_table('main', transform_main_res)
        
        logger.info(f'ETL process complete')
        sleep(300)


if __name__ == '__main__':

    logger.add("etl_debug.log", format="{time} {level} {message}", level="INFO", rotation="1 MB")

    # Create tables
    create_main()
    create_registration()

    # main etl process
    try:
        with sqlite_connector("../database.db") as sqlite_conn:
            etl(sqlite_conn)
    except Exception as exc:
        logger.error(f"{exc}")
