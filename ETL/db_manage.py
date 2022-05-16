import sqlite3


def drop_table():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE main")
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
    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registration LIMIT 5")
    result = cursor.fetchall()
    print(result)
    conn.close()


def create_main():
    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS main (
        date DATE,
        name TEXT NOT NULL,
        chaturbate INTEGER,
        camsoda INTEGER,
        mfc INTEGER,
        stripchat INTEGER,
        jasmin FLOAT,
        streamate FLOAT);""")
    conn.close()


def create_registration():
    conn = sqlite3.connect("../database.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS registration (
        id INTEGER UNIQUE,
        name TEXT NOT NULL UNIQUE,
        chat_id INTEGER);""")
    conn.close()


if __name__ == "__main__":
    # delete_from_logins()
    # create_main()
    # create_registration()
    select_all_logins()
    # drop_table()
