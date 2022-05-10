
def name_by_chat_id(connection, chat_id):
        cursor = connection.cursor()
        # Ищем имя модели по id беседы
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
