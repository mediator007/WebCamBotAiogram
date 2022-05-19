import datetime
import time
from utils.local_vars import admin_pass, cells_for_sum, bonus_table
from loguru import logger
from aiogram.dispatcher.filters.state import State, StatesGroup


class OrderDeals(StatesGroup):
    """
    Состояния для конечного автомата
    """
    waiting_for_ID = State()
    waiting_for_admindeals = State()
    waiting_for_modeldeals = State()
    waiting_for_model_add = State()
    waiting_for_model_delete = State()
    waiting_for_date = State()
    waiting_for_report = State()
    waiting_for_report_sum = State()


def sum_for_week(rows):
    """
    Считает сумму по строкам из бд
    """
    week_sum = []
    for row in rows:
        row = list(row)
        for i in range(len(row)):
            if row[i] is None:
                row[i] = 0
        sum_for_day = (0.05 * (
            row[2] +
            row[3] +
            row[4] +
            row[5]
            ) +
            row[6] + 
            row[7]
            ) * 0.5  # Добавить остальные поля
        week_sum.append(sum_for_day)
    return sum(week_sum)


def bonus(balance):
    """
    Расчет остатка до бонуса
    """
    for i in range(300, 800, 50):
        if i > balance:
            message = f"Остаток до бонуса {bonus_table[i]}% составляет {i - balance:.2f}$"
            break
    return message