from db import get_connection

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM PROJECT;")
print(cursor.fetchall())
conn.close()
