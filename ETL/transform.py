from ETL.backoff import backoff
from dataclasses import dataclass
from datetime import datetime
from services import empty_str_to_null
from loguru import logger

logger.add("../debug.log", format="{time} {level} {message}", level="INFO", rotation="1 MB")


@dataclass
class MainData:
    date: datetime.date
    name: str
    chaturbate: int
    camsoda: int
    mfc: int
    stripchat: int
    jasmin: float
    streamate: float


@dataclass
class RegistrationData:
    name: str
    id: int


@backoff()
def main_transform(data: tuple) -> tuple:
    result_list = []

    for element in data:
        try:
            result_object = MainData(
                datetime.strptime(element["Дата"], '%d.%m.%Y'),
                element["42"],
                empty_str_to_null(element["Chaturbate (tks)"]),
                empty_str_to_null(element["CamSoda"]),
                empty_str_to_null(element["MFC (tks)"]),
                empty_str_to_null(element["Stripchat (tks)"]),
                empty_str_to_null(element["Jasmin"]),
                empty_str_to_null(element["Streamate"])
            )
            result_list.append(result_object)
        except Exception as exc:
            logger.error(f"In date: {element['Дата']} name: {element['42']} Error: {exc}")

    result = tuple(result_list)
    return result


@backoff()
def registration_transform(data: tuple) -> tuple:
    result_list = []

    for element in data:
        result_object = RegistrationData(
            element["Name"],
            element[" ID"]
        )
        result_list.append(result_object)

    result = tuple(result_list)
    return result
