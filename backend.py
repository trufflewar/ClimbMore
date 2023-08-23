import sqlite3
import datetime
import dbaccess as db


#ACCOUNT, CUSTOMER, INSTRUCTOR MANAGEMENT

#Add new staff member
def addNewStaff(username, password, name, email, pay, certs = [], admin = False):
    #Set Admin integers
    if admin == True:
        admin = 3
    else:
        admin = 2

    #Create account record, get respective accountID, and create corresponding instructor entry
    db.executeSQL('INSERT INTO Accounts (username, password, permissions) VALUES (?, ?, ?) ', (username, password, admin))
    accountID = db.executeSQL('SELECT accountID FROM Accounts WHERE username = ?', (username,))[0][0]
    db.executeSQL('INSERT INTO Instructors (accountID, name, email, pay) VALUES (?, ?, ?, ?)', (accountID, name, email, pay))

    #Get all certification names
    certsFile = open('instructorcerts.txt').read()
    certList = certsFile.split('\n')
    certList.remove('')
    
    #Changes all specified certification columns to 1
    for cert in certs:
        if cert in certList:
            db.executeSQL(f'UPDATE Instructors SET {cert} = 1 WHERE accountID = ?', (accountID,))
    

#add new customer
def addNewCustomer(username, password, fname, sname, email, DOB):
    
    #Create account record, get respective accountID, and create corresponding custmer entry
    db.executeSQL('INSERT INTO Accounts (username, password, permissions) VALUES (?, ?, 1) ', (username, password))
    accountID = db.executeSQL('SELECT accountID FROM Accounts WHERE username = ?', (username,))[0][0]
    db.executeSQL('INSERT INTO Customers (accountID, fname, sname, email, DOB) VALUES (?, ?, ?, ?, ?)', (accountID, fname, sname, email, DOB))


#login
def login(username, password):
    #get corresponding pwd and ID if exist
    details = db.executeSQL('SELECT accountID, password, permissions FROM Accounts WHERE username = ?', (username,))

    #check username exists
    if len(details)==1:
         details = details[0]
    else:
         return 'WrongUsername'

    #check password
    if details[1] == password:
        return 'LoggedIn' + str(details[0])
    else:
        return 'WrongPassword'
    

#change account password
def changePassword(username, oldPassword, newPassword):
    loginCheck = login(username, oldPassword)
    if loginCheck[:8]=='LoggedIn':
        db.executeSQL('UPDATE Accounts SET password = ? WHERE accountID = ?', (newPassword, int(loginCheck[8:])))
        return 'ChangedPassword'
    else:
        return loginCheck


#search for an instructor
def getInstructor(accountID = None, instructorID = None, name = None, email = None, pay = None, certs = None):
    searchParams = locals() #this is a very messy way of doing it :/
    del searchParams['certs']

    for cert in certs:
        searchParams[cert] = 1
    
    command = 'SELECT * FROM Instructors WHERE '
    values = []

    for parameter in searchParams: #MORE messy!
        if searchParams[parameter] != None:
            command = command + parameter + ' = ? AND '
            values.append(searchParams[parameter])

    command = command[:(len(command)-4)]
    results = db.executeSQL(command, tuple(values))
    return results


def getCustomer(accountID = None, customerID = None, fname = None, sname = None, email = None, DOB = None):
    searchParams = locals()

    command = 'SELECT * FROM Customers WHERE '
    values = []

    for parameter in searchParams: #MORE messy!
        if searchParams[parameter] != None:
            command = command + parameter + ' = ? AND '
            values.append(searchParams[parameter])

    command = command[:(len(command)-4)]
    #print(command)
    results = db.executeSQL(command, tuple(values))
    return results

def getPermissions(accountID):
    return int(db.executeSQL('SELECT permissions FROM Accounts WHERE accountID = ?', (accountID,))[0][0])


#edit instructor details - uses same systems as get instructor but constructs SQL to edit instead
def editInstructor(instructorID, name = None, email = None, pay = None, certs = []):
    #gets all arguments and removes instructor ID and certs
    editParams = locals()
    del editParams['instructorID']
    del editParams['certs']

    #replaces the certs back into the editParams list as separate items
    certsFile = open('instructorcerts.txt').read()
    certList = certsFile.split('\n')
    certList.remove('')
    for cert in certList:
        if cert in certs:
            editParams[cert] = 1
        else:
            editParams[cert] = 0

    #Setup command
    command = 'UPDATE Instructors SET '
    values = []

    #construct statement, finish it, and execute
    for parameter in editParams:
        if editParams[parameter] != None:
            command = command + parameter + ' = ?, '
            values.append(editParams[parameter])

    command = command[:(len(command)-2)]

    command = command + ' WHERE instructorID = ? '
    values.append(instructorID)

    db.executeSQL(command, tuple(values))


#same as edit Instructor without certs parts of the code
def editCustomer(customerID, fname = None, sname = None, email = None, DOB = None):
    editParams = locals()
    del editParams['customerID']

    command = 'UPDATE Customers SET '
    values = []

    for parameter in editParams:
        if editParams[parameter] != None:
            command = command + parameter + ' = ?, '
            values.append(editParams[parameter])

    command = command[:(len(command)-2)]

    command = command + ' WHERE customerID = ? '
    values.append(customerID)

    db.executeSQL(command, tuple(values))


#The following remove subroutines will be expaned to also delete respective bookings, rentals, assignments etc
def removeInstructor(instructorID):
    accountID = db.executeSQL('SELECT accountID FROM Instructors WHERE instructorID = ?', (instructorID,))[0][0]
    db.executeSQL('DELETE FROM Instructors WHERE instructorID = ?', (instructorID,))
    db.executeSQL('DELETE FROM Accounts WHERE accountID = ?', (accountID,))
    
def removeCustomer(customerID):
    accountID = db.executeSQL('SELECT accountID FROM Customers WHERE customerID = ?', (customerID,))[0][0]
    db.executeSQL('DELETE FROM Customers WHERE customerID = ?', (customerID,))
    db.executeSQL('DELETE FROM Accounts WHERE accountID = ?', (accountID,))


#add cterification column in instructors - BIG FLAW HERE - this i vunerable to SQL injection and
#needs some code to sanitise inputs    
def addCertType(certName, default = False):
    if default==True:
        default = 1
    else:
        default = 0

    db.executeSQL(f'''ALTER TABLE Instructors ADD COLUMN {certName} INTEGER NOT NULL DEFAULT {default}
                    CHECK({certName} IS 0 OR {certName} IS 1)''')

    
