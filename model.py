import sqlite3 as db

def make_connection(dbname):
    return db.connect(dbname)

def dump_registration(form, connection):
    print form.values()
    cursor = connection.cursor()
    sqlquery = "INSERT INTO registration VALUES('{title}', '{surname}', '{name}', '{institut}', \
             '{city}', '{country}', '{email}', '{ptitle}', '{pabstract}', '{ptype}', '{pcomment}');".format(**form)
    print sqlquery
    cursor.execute(sqlquery)
    connection.commit()