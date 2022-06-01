import sqlite3
# sqlite3 -column -header database.db

from datetime import date
import datetime
import time

def name_by_chat_id(connection, chat_id):
    """
    Получение имени модели по chat_id
    """
    cursor = connection.cursor()
    cursor.execute("""SELECT name FROM registration WHERE chat_id = ?""", (chat_id,))
    result = cursor.fetchone()
    return result


def name_by_input_id(connection, input_id):
    """
    Получение имени модели по введенному id
    """
    cursor = connection.cursor()
    cursor.execute("""SELECT name FROM registration WHERE id = ?""", (input_id,))
    result = cursor.fetchone()
    return result


def update_chat_id_in_registration(connection, chat_id, id):
    """
    Запись модели в бд для ребута
    """
    cursor = connection.cursor()
    cursor.execute("""UPDATE registration SET chat_id = ? WHERE id = ?""", (chat_id, id,))
    connection.commit()


def delete_from_registration(connection, chat_id):
    """
    Log out для модели
    """
    cursor = connection.cursor()
    cursor.execute("""UPDATE registration SET chat_id = NULL WHERE chat_id = ?""", (chat_id,))
    connection.commit()


def week_result_rows(connection, date, name):
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM main WHERE date > ? AND name = ?""", (date, name,))
    result = cursor.fetchall()
    return result


def add_report(connection, current_date, name, site, value):
    """
    Запись в бд отчета за текущую дату для одного сайта
    """
    cursor = connection.cursor()
    check = cursor.execute("""SELECT * FROM main WHERE date = ? AND name = ?""", (current_date, name))
    check = cursor.fetchall()
    # If was any reports in CURRENT date
    if check:
        line = f"""UPDATE main SET {site} = {value} WHERE date = ? AND name = ?"""
        cursor.execute(line, (current_date, name,))
        connection.commit()
    # If its first report by CURRENT day
    else:
        line = f"""INSERT INTO main (date, name, {site}) VALUES (?, ?, ?)"""
        cursor.execute(line, (current_date, name, value))
        connection.commit()


def rows_for_week(connection, name):
    """
    Получаем все записи от понедельника текущей недели для модели
    """
    # Дата понедельника текущей недели
    monday_date = date.today() - datetime.timedelta(days=date.today().isoweekday() % 7 - 1)
    cursor = connection.cursor()
    result = cursor.execute("""SELECT * FROM main WHERE date >= ? AND name = ?;""", (monday_date, name,))
    result = cursor.fetchall()
    return result


def add_admin_to_db(chat_id):
    """
    Add admin chat_id to DB(admin_registration) for forwarding reports from models
    """
    sql_request = f"""INSERT INTO admin_registration (chat_id) VALUES (?)"""
    execute_function(sql_request, chat_id)


def delete_admin_from_db(chat_id):
    """
    Delete admin chat_id from DB(admin_registration) for stop forwarding reports from models
    """
    sql_request = f"""DELETE FROM admin_registration WHERE chat_id = ?;"""
    execute_function(sql_request, chat_id)


def get_admin_list():
    """
    Список админов для рассылки отчета прие его отправлении моделью
    """
    sql_request = """SELECT chat_id FROM admin_registration;"""
    return return_function(sql_request)


def search_admin_for_reboot(chat_id):
    """
    Поиск админа в БД для восстановлении сессии при ребуте
    """
    sql_request = """SELECT * FROM admin_registration WHERE chat_id = ?;"""
    return return_function(sql_request, chat_id)


def cur_date_report_for_admin():
    """
    Report for admin by current date
    """
    current_date = datetime.date.today()
    sql_request = """SELECT * FROM main WHERE date = ?;"""
    return return_function(sql_request, current_date)


def date_report_for_admin(selected_date):
    """
    Report for admin by selected date
    """
    sql_request = """SELECT * FROM main WHERE date = ?;"""
    return return_function(sql_request, selected_date)


def get_model_list() -> list:
    """
    Return list of registered models
    """
    sql_request = """SELECT name, id FROM registration;"""
    return return_function(sql_request)


def add_model(name, rand_id):
    """
    Add model to registration
    """
    sql_request = """INSERT INTO registration (name, id) VALUES (?, ?);"""
    execute_function(sql_request, name, rand_id)


def check_id() -> list:
    """
    Возвращает все айди моделей для проверки уникальности созданного
    """
    sql_request = """SELECT id FROM registration;"""
    return return_function(sql_request)


def model_name_list() -> list:
    """
    Возвращает все айди моделей для проверки уникальности созданного
    """
    sql_request = """SELECT name FROM registration;"""
    return return_function(sql_request)


def delete_model(name):
    """
    Delete model from registration
    """
    sql_request = """DELETE FROM registration WHERE name = ?;"""
    execute_function(sql_request, name)


def check_model_auth(input_id):
    """
    Check is model auth already, to prevent double registration
    """
    sql_request = """SELECT chat_id FROM registration WHERE id = ?;"""
    print("inid", input_id)
    return return_function(sql_request, input_id)


def execute_function(sql_request, *args):
    with sqlite3.connect("./database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(sql_request, args)
        conn.commit()


def return_function(sql_request, *args):
    with sqlite3.connect("./database.db") as conn:
        cursor = conn.cursor()
        cursor.execute(sql_request, args)
        result = cursor.fetchall()
        print("!!!", result)
        return result
