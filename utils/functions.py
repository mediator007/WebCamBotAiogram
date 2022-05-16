import datetime
import time
from utils.local_vars import admin_pass, cells_for_sum, bonus_table
from loguru import logger
# from db_requests import week_result
from aiogram.dispatcher.filters.state import State, StatesGroup


class OrderDeals(StatesGroup):
    waiting_for_ID = State()
    waiting_for_admindeals = State()
    waiting_for_modeldeals = State()
    waiting_for_modeldelete = State()
    waiting_for_date = State()
    waiting_for_report = State()


def admin_search(admin_id):
    """
    Проверка админского айдишника
    """
    if admin_id == admin_pass:
        search_res = True
    else:
        search_res = False
    return search_res


def sum_for_week(result, Name):
    # Получаем день, месяц , год сегодняшней даты
    now = [time.localtime()[0], time.localtime()[1], time.localtime()[2]]
    # Получаем номер недели нынешней даты
    NowWeeknumber = datetime.date(now[0], now[1], now[2]).isocalendar()[1]
    # Массив для записи суммы для девочки за неделю
    SummForWeek = []
    for i in range(len(result)):
        if result[i]['42'] == Name:
            a = result[i]['Дата']
            # разделяет строку по разделителю - точке
            b = a.split('.')
            DateForCheck = []
            for j in b:
                if j.isdigit():
                    DateForCheck.append(int(j))
            DateForCheck.reverse()
            try:
                # Получаем номер недели даты в строке
                weeknumber = datetime.date(DateForCheck[0], DateForCheck[1], DateForCheck[2]).isocalendar()[1]
            except Exception as e:
                # Если дата админом поставлена неверно
                logger.error(f"Неверно установлена дата - {e}")
            if NowWeeknumber == weeknumber:
                for name in cells_for_sum:
                    # если в документе пустые ячейки, заменяет Нулями
                    if result[i][name] == '':
                        result[i][name] = 0
                    elif type(result[i][name]) == str:
                        result[i][name] = 0
                SummForDay = (0.05 * (
                        result[i]['Chaturbate (tks)']
                        + result[i]['CamSoda']
                        + result[i]['MFC (tks)']
                        + result[i]['Stripchat (tks)']
                )
                              + result[i]['Jasmin'] + result[i]['Streamate']) * 0.5  # Добавить остальные поля!!!
                SummForWeek.append(SummForDay)
            else:
                i += 1
    return sum(SummForWeek)


def bonus(balance):
    """

    """
    for i in range(300, 800, 50):
        if i > balance:
            message = f"Остаток до бонуса {bonus_table[i]}% составляет {i - balance}$"
            break
    return message


if __name__ == "__main__":
    pass