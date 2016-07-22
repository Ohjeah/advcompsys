import sqlite3
import csv

from app import DB_NAME, DB_TABLE


if __name__ == "__main__":
    query = "SELECT * FROM {0};".format(DB_TABLE)
    with sqlite3.connect(DB_NAME) as con:
        result = con.cursor().execute(query)

    with open("{0}.csv".format(DB_TABLE), 'w') as f:
        writer = csv.writer(f)
        writer.writerows(result)
