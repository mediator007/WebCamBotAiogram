import sqlite3

conn = sqlite3.connect("database.db") ##
cursor = conn.cursor()

cursor.execute("DELETE FROM logins")
conn.commit()
conn.close

cursor.execute("SELECT * FROM logins")
print(cursor.fetchall())