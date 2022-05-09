from ETL.backoff import backoff
from dataclasses import dataclass
from datetime import datetime
from services import data_values_to_dataclass


@dataclass
class Main_data:
    date: datetime.date
    name: str
    chaturbate: int
    camsoda: int
    mfc: int
    stripchat: int
    jasmin: float
    streamate: float

def empty_str_to_null(str):
    if str == '':
        return 0
    else:
        return str

@backoff()
def main_transform(data: tuple) -> tuple:
    result_list = []
    
    for element in data:
        result_dict = {
            "date": datetime.strptime(element["Дата"], '%d.%m.%Y'), 
            "name": element["42"], 
            "chaturbate": empty_str_to_null(element["Chaturbate (tks)"]),
            "camsoda": empty_str_to_null(element["CamSoda"]), 
            "mfc": empty_str_to_null(element["MFC (tks)"]),
            "stripchat": empty_str_to_null(element["Stripchat (tks)"]), 
            "jasmin": empty_str_to_null(element["Jasmin"]),
            "streamate": empty_str_to_null(element["Streamate"])
            }
        
        result_object = data_values_to_dataclass(Main_data, result_dict)
        
        result_list.append(result_dict)

    print(type(result_object.date))
    result = tuple(result_list)
    return result


@backoff()
def registration_transform(data: tuple) -> tuple:
    result_list = []
    
    for element in data:
        result_dict = {"name": element["Name"], "id": element[" ID"]}
        result_list.append(result_dict)
    
    result = tuple(result_list)
    
    return result