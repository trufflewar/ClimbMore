import sqlite3

# this file is used to remove requiremtnt for conn configuration etc in backend.py


def getPath():
    pathFile = open('path.txt', 'r')
    read = pathFile.read()
    pathFile.close()
    return read
    

def executeSQL(command, valueTuple = (), returnCursor = False):

    conn = sqlite3.connect(getPath())
    c = conn.cursor()

    c.execute(command, valueTuple)
    dboutput = c.fetchall()

    if returnCursor==True and not dboutput:
        dboutput = c.lastrowid

    conn.commit()
    conn.close()

    return dboutput
