import datetime
import time
import local_vars


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
    if admin_id == local_vars.admin_pass:
        admin_search = True
    else:
        admin_search = False
    return admin_search


def Sum_for_week(result, Name):
    now = [time.localtime()[0], time.localtime()[1], time.localtime()[2]]  # Получаем день, месяц , год сегодняшней даты
    NowWeeknumber = datetime.date(now[0], now[1], now[2]).isocalendar()[1]  # Получаем номер недели нынешней даты
    SummForWeek = []  # Массив для записи суммы для девочки за неделю
    for i in range(len(result)):
        if result[i]['42'] == Name:
            a = result[i]['Дата']
            b = a.split('.')  # разделяет строку по разделителю - точке
            DateForCheck = []
            for j in b:
                if j.isdigit():
                    DateForCheck.append(int(j))
            DateForCheck.reverse()
            try:
                Weeknumber = datetime.date(DateForCheck[0], DateForCheck[1], DateForCheck[2]).isocalendar()[1]  # Получаем номер недели даты в строке
                # print(Weeknumber)
            except Exception as e:
                print(e)
                print("Неверное заполнение даты в таблице")  # Если дата админом поставлена неверно
            if NowWeeknumber == Weeknumber:
                for name in local_vars.cells_for_sum:
                    if result[i][name] == '':  # если в документе пустые ячейки, заменяет Нулями
                        result[i][name] = 0
                    elif type(result[i][name]) == str:
                        result[i][name] = 0
                SummForDay = (0.05 * ( \
                            result[i]['Chaturbate (tks)']
                            + result[i]['CamSoda']
                            + result[i]['MFC (tks)']
                            + result[i]['Stripchat (tks)'] \
                    ) \
                              + result[i]['Jasmin'] + result[i]['Streamate']) * 0.5  # Добавить остальные полЯЯ!!!
                SummForWeek.append(SummForDay)
            else:
                i += 1
    return sum(SummForWeek)


def bonus(balance):
    for i in range(300, 800, 50):
        if i > balance:
            message = f"Остаток до бонуса {local_vars.bonus_table[i]}% составляет {i - balance}$"
            break
    return message
