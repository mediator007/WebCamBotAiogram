from ETL.backoff import backoff

@backoff()
def main_transform(data: tuple) -> tuple:
    result_list = []
    
    for element in data:
        result_dict = {}
        result_dict["date"] = element["Дата"]
        result_dict["name"] = element["42"]
        result_dict["chaturbate"] = element["Chaturbate (tks)"]
        result_dict["camsoda"] = element["CamSoda"]
        result_dict["mfc"] = element["MFC (tks)"]
        result_dict["stripchat"] = element["Stripchat (tks)"]
        result_dict["jasmin"] = element["Jasmin"]
        result_dict["streamate"] = element["Streamate"] 
        result_list.append(result_dict)
    
    result = tuple(result_list)
    return result

@backoff()
def registration_transform(data: tuple) -> tuple:
    result_list = []
    
    for element in data:
        result_dict = {}
        result_dict["id"] = element[" ID"] # Пробел перед ID
        result_dict["name"] = element["Name"] 
        result_list.append(result_dict)
    
    result = tuple(result_list)
    
    return result