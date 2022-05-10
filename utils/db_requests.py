import sqlite3

def name_by_chat_id(connection, chat_id):
    cursor = connection.cursor()
    cursor.execute("""SELECT name FROM registration WHERE chat_id = ?""", (chat_id,))
    result = cursor.fetchone()
    return result


def name_by_input_id(connection, input_id):
    cursor = connection.cursor()
    cursor.execute("""SELECT name FROM registration WHERE id = ?""", (input_id,))
    result = cursor.fetchone()
    return result


def update_chat_id_in_registration(connection, chat_id, id):
    cursor = connection.cursor()
    cursor.execute("""UPDATE registration SET chat_id = ? WHERE id = ?""", (chat_id, id,))
    connection.commit()


def delete_from_registration(connection, chat_id, ):
    cursor = connection.cursor()
    cursor.execute("""UPDATE registration SET chat_id = NULL WHERE chat_id = ?""", (chat_id,))
    connection.commit()


def week_result_rows(connection, date, name):
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM main WHERE date > ? AND name = ?""", (date, name,))
    result = cursor.fetchall()
    return result

if __name__ == "__main__":
    
    with sqlite3.connect("../database.db") as conn:
        res = week_result_rows(conn, '2022-05-01', "Marzia")
        print(res)
