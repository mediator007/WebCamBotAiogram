import sqlite3
# sqlite3 -column -header database.db

from datetime import date

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


def delete_from_registration(connection, chat_id, ):
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
    if check:
        line = f"""UPDATE main SET {site} = {value} WHERE date = ? AND name = ?"""
        # UPDATE main SET chaturbate  = 777 WHERE date = "2022-05-04 00:00:00" AND  name = "Lisa";
        cursor.execute(line, (current_date, name,))
        connection.commit()
    else:
        line = f"""INSERT INTO main (date, name, {site}) VALUES (?, ?, ?)"""
        cursor.execute(line, (current_date, name, value))
        connection.commit()

# if __name__ == "__main__":
#     current_date = date.today()
#     print(current_date)
#     with sqlite3.connect("../database.db") as conn:
#         add_report(conn, current_date, "Marzia", "jasmin", 123)
#         print(res)
