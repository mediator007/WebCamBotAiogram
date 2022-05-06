from time import sleep

from loguru import logger

from connections import sqlite_connector
from export import GDriveExport
from transform import main_transform, registration_transform
from load import SqliteLoader

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
        transform_regitration_res = registration_transform(registration_result)
        transform_main_res = main_transform(main_result)

        # Load
        # loader = SqliteLoader(connector)

        print("registration", transform_regitration_res[0])
        print("main", transform_main_res[0])
        sleep(300)


if __name__ == '__main__':
    logger.add("etl_debug.log", format="{time} {level} {message}", level="INFO", rotation="1 MB")

    # try:
    with sqlite_connector("etl_database.db") as sqlite_conn:
        etl(sqlite_conn)
    # except Exception as exc:
    #     logger.error(f"{exc}")