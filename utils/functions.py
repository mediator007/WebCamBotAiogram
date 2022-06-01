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
    week_sum_list = []
    for row in rows:
        row = list(row)
        for i in range(len(row)):
            if row[i] is None:
                row[i] = 0
        sum_for_day = (
            0.05 * (row[2] + row[3] + row[4] + row[5]) + 
            row[6] + row[7]
            )
        week_sum_list.append(sum_for_day)
    week_sum = sum(week_sum_list)
    return week_sum


def bonus(week_sum):
    """
    Расчет бонуса
    """
    if week_sum < 300:
        return 50
    
    for i in range(350, 800, 50):
        if i > week_sum:
            return bonus_table[i-50]
    
    if week_sum >= 750:
        return bonus_table[750]


def for_next_bonus(week_sum):
    """
    Расчет остатка до следующего бонуса
    """
    if week_sum < 300:
        remains = 300 - week_sum
        return remains
    
    for i in range(350, 800, 50):
        if i > week_sum:
            remains = i - week_sum
            return remains
    
    if week_sum >= 750:
        return 0