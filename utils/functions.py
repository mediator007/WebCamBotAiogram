import datetime
import time

from loguru import logger
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.utils.callback_data import CallbackData

from utils.local_vars import (
    admin_pass, 
    cells_for_sum, 
    bonus_table, 
    available_work_buttons,
    available_sites_buttons,
    )


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
            0.05 * (row[2] + row[3] + row[4] + row[5] + row[8]) + 
            row[6] + row[7]
            )
        week_sum_list.append(sum_for_day)
    week_sum = sum(week_sum_list)
    return week_sum


def bonus(week_sum):
    """
    Расчет бонуса
    """
    if week_sum < 400:
        return 50
    
    for i in range(450, 900, 50):
        if i > week_sum:
            return bonus_table[i-50]
    
    if week_sum >= 850:
        return bonus_table[850]


def for_next_bonus(week_sum):
    """
    Расчет остатка до следующего бонуса
    """
    if week_sum < 400:
        remains = 400 - week_sum
        return remains
    
    for i in range(450, 900, 50):
        if i > week_sum:
            remains = i - week_sum
            return remains
    
    if week_sum >= 850:
        return 0


def create_keyboard(buttons_list: list) -> types.ReplyKeyboardMarkup:
    """
    Create ReplyKeyboardMarkup markup
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons_list:
        markup.add(button)
    return markup


sites_cb = CallbackData('vote', 'action')  # vote:<action>

def get_keyboard():
    """
    Create InlineKeyboardMarkup
    """
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    row_btns_1 = (
        types.InlineKeyboardButton(available_sites_buttons[0], callback_data=sites_cb.new(action=available_sites_buttons[0])),
        types.InlineKeyboardButton(available_sites_buttons[1], callback_data=sites_cb.new(action=available_sites_buttons[1])),
        types.InlineKeyboardButton(available_sites_buttons[2], callback_data=sites_cb.new(action=available_sites_buttons[2])),
    )
    row_btns_2 = (
        types.InlineKeyboardButton(available_sites_buttons[3], callback_data=sites_cb.new(action=available_sites_buttons[3])),
        types.InlineKeyboardButton(available_sites_buttons[4], callback_data=sites_cb.new(action=available_sites_buttons[4])),
        types.InlineKeyboardButton(available_sites_buttons[5], callback_data=sites_cb.new(action=available_sites_buttons[5])),
    )
    row_btns_3 = (
        types.InlineKeyboardButton(available_sites_buttons[6], callback_data=sites_cb.new(action=available_sites_buttons[6])),
    )
    keyboard_markup.row(*row_btns_1)
    keyboard_markup.row(*row_btns_2)
    keyboard_markup.row(*row_btns_3)
    return keyboard_markup