import sqlite3


def drop_table():
    conn = sqlite3.connect("etl_database.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE registration")
    conn.commit()
    conn.close()


def delete_from_logins():
    conn = sqlite3.connect("etl_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registration")
    print("logins are Empty")
    conn.commit()
    conn.close()


def select_all_logins():
    conn = sqlite3.connect("etl_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM main LIMIT 5")
    result = cursor.fetchall()
    print(result)
    conn.close()


if __name__ == "__main__":
    # delete_from_logins()
    select_all_logins()
    # drop_table()
