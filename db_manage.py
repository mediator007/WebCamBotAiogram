import sqlite3


def delete_from_logins():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logins")
    print("logins are Empty")
    conn.commit()
    conn.close()


def select_all_logins():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM logins")
    result = cursor.fetchall()
    print(result)


if __name__ == "__main__":
    # delete_from_logins()
    select_all_logins()
