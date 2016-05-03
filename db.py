import sqlite3

dbname = "db.db"

connection = sqlite3.connect(dbname)
cursor = connection.cursor()

for row in cursor.execute("SELECT * from registration"):
	print(row)