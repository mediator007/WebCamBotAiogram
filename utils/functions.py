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
    waiting_for_report_sum = State()


def admin_search(admin_id):
    """
    Проверка админского айдишника
    """
    if admin_id == admin_pass:
        search_res = True
    else:
        search_res = False
    return search_res


def sum_for_week(rows):
    """
    Считает сумму по строкам из бд
    """
    week_sum = []
    for row in rows:
        sum_for_day = (0.05 * (
            result[i]['Chaturbate (tks)'] +
            result[i]['CamSoda'] +
            result[i]['MFC (tks)'] +
            result[i]['Stripchat (tks)']
            ) +
            result[i]['Jasmin'] + 
            result[i]['Streamate']
            ) * 0.5  # Добавить остальные поля!!!
        week_sum.append(sum_for_day)
    return sum(week_sum)


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