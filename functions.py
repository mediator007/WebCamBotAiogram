import datetime
import time
import vars

def search_id(massiv, id):  ###поиск айдишника В ДОКУМЕНТЕ РЕГИСТРАЦИИ
    for i in range(len(massiv)):  
        if id == massiv[i][' ID']: 
            search = True
            break
        else:
            search = False
    return search

def search_name(massiv, id):  ###поиск имени В ДОКУМЕНТЕ РЕГИСТРАЦИИ
    for i in range(len(massiv)):  
        if id == massiv[i][' ID']: 
            Name = massiv[i]['Name']
            break
        else:
            i += 1
    return Name

def admin_search(admin_id):  ### проверка админского айдишника
    if admin_id == vars.admin_pass: 
        admin_search = True
    else:
        admin_search = False
    return admin_search


def Sum_for_week(result, Name):
    now = [time.localtime()[0], time.localtime()[1], time.localtime()[2]] # Получаем день, месяц , год сегодняшней даты
    NowWeeknumber = datetime.date(now[0], now[1], now[2]).isocalendar()[1] # Получаем номер недели нынешней даты
    SummForWeek = [] #Массив для записи суммы для девочки за неделю
    for i in range(len(result)):
        if result[i]['42'] == Name:
            a = result[i]['Дата']
            b = a.split('.')#разделяет строку по разделителю - точке
            DateForCheck = []
            for j in b:
                if(j.isdigit()):
                    DateForCheck.append(int(j))
            DateForCheck.reverse()
            try:
                Weeknumber = datetime.date(DateForCheck[0], DateForCheck[1], DateForCheck[2]).isocalendar()[1] # Получаем номер недели даты в строке
                #print(Weeknumber)
            except Exception as e:
                print(e)
                print("Неверное заполнение даты в таблице") # Если дата админом поставлена неверно
            if NowWeeknumber == Weeknumber:
                SummForDay = (0.05*(\
                result[i]['Chaturbate (tks)'] \
                + result[i]['CamSoda'] \
                + result[i]['MFC (tks)'] \
                + result[i]['Stripchat (tks)'] \
                ) \
                + result[i]['Jasmin'] + result[i]['Streamate']) * 0.5 ### Добавить остальные полЯЯ!!!
                SummForWeek.append(SummForDay)
            else:
                i += 1
    return sum(SummForWeek)

################
bonus_table = {
    300:51, 350:52, 400:53, 450:54, 500:55,\
    550:56, 600:57, 650:58, 700:59, 750:60
    }
###############

def bonus(balance):
    for i in range(300, 800, 50):
        if i > balance:
            message = f"Остаток до бонуса {bonus_table[i]}% составляет {i - balance}$"
            break
    return message

   