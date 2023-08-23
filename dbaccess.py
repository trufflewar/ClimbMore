import sqlite3

# this file is used to remove requiremtnt for conn configuration etc in backend.py


def getPath():
    pathFile = open('path.txt', 'r')
    return pathFile.read()
    pathFile.close()
    

def executeSQL(command, valueTuple = ()):

    conn = sqlite3.connect(getPath())
    c = conn.cursor()

    c.execute(command, valueTuple)
    dboutput = c.fetchall()

    conn.commit()
    conn.close()

    return dboutput
