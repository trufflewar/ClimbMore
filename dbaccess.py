import sqlite3

# this file is used to remove requiremtnt for conn configuration etc in backend.py
#TODO potential error chekcing for missing file in getPath()

def getPath():
    #retrieve file path
    pathFile = open('path.txt', 'r')
    read = pathFile.read()
    pathFile.close()
    return read
    

def executeSQL(command, valueTuple = (), returnCursor = False):
    #create connection
    conn = sqlite3.connect(getPath())
    c = conn.cursor()

    #execute command and retrieve results
    c.execute(command, valueTuple)
    dboutput = c.fetchall()

    #return cursor if required
    if returnCursor==True and not dboutput:
        dboutput = c.lastrowid

    #commit commnad and close connection
    conn.commit()
    conn.close()

    return dboutput
