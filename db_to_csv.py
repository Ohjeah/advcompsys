import sqlite3
import csv
import re

from app import DB_NAME, DB_TABLE

patterns = re.compile("[Tt]est"), re.compile("[Qq]uade")


def no_test_row(row):
    return not any(re.findall(pattern, s) for pattern in patterns for s in row)


def encode(row, exclude=(8,)):
    return [s.encode('utf-8') for i, s in enumerate(row) if i not in exclude]


if __name__ == "__main__":
    query = "SELECT * FROM {0};".format(DB_TABLE)
    with sqlite3.connect(DB_NAME) as con:
        result = con.cursor().execute(query)

    result = set(map(tuple, result))  # filter duplicates
    result = map(encode, filter(no_test_row, result)) # remove tests and encode to utf

    with open("{0}.csv".format(DB_TABLE), 'w') as f:
        writer = csv.writer(f)
        writer.writerows(result)
