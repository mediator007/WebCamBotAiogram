from ETL.backoff import backoff


@backoff()
def main_transform(data: tuple) -> tuple:
    result_list = []
    
    for element in data:
        result_dict = {"date": element["Дата"], "name": element["42"], "chaturbate": element["Chaturbate (tks)"],
                       "camsoda": element["CamSoda"], "mfc": element["MFC (tks)"],
                       "stripchat": element["Stripchat (tks)"], "jasmin": element["Jasmin"],
                       "streamate": element["Streamate"]}
        result_list.append(result_dict)
    
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