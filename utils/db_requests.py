# class DBRequests(connection):
    
#     def __init__(self, connection):
#         self.connection = connection
    
def is_chat_id_exist(connection, chat_id):
        cursor = connection.cursor()
        # Ищем имя модели по id беседы
        cursor.execute("SELECT name FROM registration WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False

def is_input_id_relevant(connection, input_id):
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM registration WHERE id = ?", (input_id,))
    result = cursor.fetchone()
    return result
