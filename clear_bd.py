import sqlite3

conn = sqlite3.connect("database.db") ##
cursor = conn.cursor()

cursor.execute("DELETE FROM logins")
conn.commit()

cursor.execute("SELECT name FROM logins")
result = cursor.fetchall()
print(result)