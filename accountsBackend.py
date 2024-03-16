#Import required modules    
import datetime
import dbaccess as db
import datetime
from argon2 import PasswordHasher
import re
from dateutil import relativedelta

ph = PasswordHasher()


#ADD NEW STAFF MEMBER
def addNewStaff(username, password, name, email, pay, certs = [], admin = False):
    #Set Admin integer values for record
    if admin == True:
        admin = 3
    else:
        admin = 2

    #Hash password
    hashed = ph.hash(password)

    #Create account record, retrieve respective accountID, and create corresponding instructor entry
    db.executeSQL('INSERT INTO Accounts (username, hash, permissions) VALUES (?, ?, ?) ', (username, hashed, admin))
    accountID = db.executeSQL('SELECT accountID FROM Accounts WHERE username = ?', (username,))[0][0]
    db.executeSQL('INSERT INTO Instructors (accountID, name, email, pay) VALUES (?, ?, ?, ?)', (accountID, name, email, pay))

    #Get all certification type names
    certsFile = open('instructorcerts.txt').read()
    certList = certsFile.split('\n')
    certList.remove('')
    
    #Changes all specified certification columns to 1 (equivalent of True)
    for cert in certs:
        if cert in certList:
            db.executeSQL(f'UPDATE Instructors SET {cert} = 1 WHERE accountID = ?', (accountID,))
    


#ADD NEW CUSTOMER
def addNewCustomer(username, password, fname, sname, email, DOB):

    hashed = ph.hash(password)
    
    #Create account record, get respective accountID, and create corresponding custmer entry
    db.executeSQL('INSERT INTO Accounts (username, hash, permissions) VALUES (?, ?, 1) ', (username, hashed))
    accountID = db.executeSQL('SELECT accountID FROM Accounts WHERE username = ?', (username,))[0][0]
    db.executeSQL('INSERT INTO Customers (accountID, fname, sname, email, DOB) VALUES (?, ?, ?, ?, ?)', (accountID, fname, sname, email, DOB))



#LOGIN (BACKEND)
def login(username, password):
    #get corresponding hash and ID if exists
    details = db.executeSQL('SELECT accountID, hash, permissions FROM Accounts WHERE username = ?', (username,))

    #check account exists   
    if len(details)==1:
         details = details[0]
    else:
         return 'WrongUsername'

    #check password
    if ph.verify(details[1], password) == True:
        return 'LoggedIn'+str(details[0])
    else:
        return 'WrongPassword'
    


#CHANGE ACCOUNT PASSWORD
def changePassword(username, oldPassword, newPassword):
    #check old password correct
    loginCheck = login(username, oldPassword)
    if loginCheck[:8]=='LoggedIn':
        #change password
        hashed = ph.hash(newPassword)
        db.executeSQL('UPDATE Accounts SET hash = ? WHERE accountID = ?', (hashed, int(loginCheck[8:])))
        return 'ChangedPassword'
    else:
        #return if failed
        return loginCheck


#CHANGE PASSWORD OVERRIDE - allows instructor to change customer password or staff to change
#                           instructor password without knowing old password 
def adminChangePassword(accountID, password):
    hashed = ph.hash(password)
    db.executeSQL('UPDATE Accounts SET hash = ? WHERE accountID = ?', (hashed, accountID))
    return 'ChangedPassword'



#SEARCH INSTRUCTORS
def getInstructor(accountID = None, instructorID = None, name = None, email = None, pay = None, certs = None):
    searchParams = locals() #get all input parameters - messy, coudl be redone using **args
    del searchParams['certs']

    #add specified certification to search parameters - not included on frontend
    if certs != None:
        for cert in certs:
            searchParams[cert] = 1

    #setup command
    command = 'SELECT * FROM Instructors WHERE '
    values = []

    #configue and add parameters to command
    for parameter in searchParams:
        if searchParams[parameter] != None:
            command = command + parameter + ' = ? AND '
            values.append(searchParams[parameter])

    #clean up and execute command
    command = command[:(len(command)-4)]
    results = db.executeSQL(command, tuple(values))
    return results



#SEARCH CUSTOMERS
def getCustomer(accountID = None, customerID = None, fname = None, sname = None, email = None, DOB = None):
    searchParams = locals()

    #setup command
    command = 'SELECT * FROM Customers WHERE '
    values = []

    #add search terms
    for parameter in searchParams: #MORE messy!
        if searchParams[parameter] != None:
            command = command + parameter + ' = ? AND '
            values.append(searchParams[parameter])

    #clean up and ecxecute
    command = command[:(len(command)-4)]
    #print(command)
    results = db.executeSQL(command, tuple(values))
    return results


#returns the permissions integer of an input account
def getPermissions(accountID):
    return int(db.executeSQL('SELECT permissions FROM Accounts WHERE accountID = ?', (accountID,))[0][0])



#CHECK IF ADULT
def checkAdult(customerID):
    #get DOB from rel acc id
    DOB = db.executeSQL('SELECT DOB FROM Customers WHERE customerID = ?', (customerID,))[0][0]

    #put into datetime form, get today date, check difference using relative delta against today
    DOB = datetime.datetime.strptime(DOB, '%Y-%m-%d')
    today = datetime.datetime.now().replace(microsecond = 0, second = 0, minute = 0, hour = 0)
    yearsOld = relativedelta.relativedelta(today, DOB).years

    #return respective boolean vlue
    if yearsOld>=18:
        return True
    else:
        return False


#EDIT INSTRUCTOR
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



#EDIT CUSTOMER - same as edit Instructor without certs parts of the code
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



# TODO 'remove'  subroutines will be expaned to also delete respective bookings, rentals, assignments etc 
#REMOVE INSTRUTCORS AND CUSTOMERS SUBROUTINES
def removeInstructor(instructorID):
    accountID = db.executeSQL('SELECT accountID FROM Instructors WHERE instructorID = ?', (instructorID,))[0][0]
    db.executeSQL('DELETE FROM Instructors WHERE instructorID = ?', (instructorID,))
    db.executeSQL('DELETE FROM Accounts WHERE accountID = ?', (accountID,))
 
def removeCustomer(customerID):
    accountID = db.executeSQL('SELECT accountID FROM Customers WHERE customerID = ?', (customerID,))[0][0]
    db.executeSQL('DELETE FROM Customers WHERE customerID = ?', (customerID,))
    db.executeSQL('DELETE FROM Accounts WHERE accountID = ?', (accountID,))



#add cterification column in instructors - TODO BIG FLAW HERE - this i vunerable to SQL injection and
#needs some code to sanitise inputs BUT is only accessible to admins...
     
#ADD INSTRUCTOR CERTIFICATION
def addCertType(certName, default = False):
    if default==True:
        default = 1
    else:
        default = 0

    db.executeSQL(f'''ALTER TABLE Instructors ADD COLUMN {certName} INTEGER NOT NULL DEFAULT {default}
                    CHECK({certName} IS 0 OR {certName} IS 1)''') #used f strig for this as easier to insert names



#EMIL VERFICATION
def verifyEmail(email):
    #uses a regex pattern to fully validate all emails input
    return bool(re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))
#TODO have this send email to check verification


#GET USERNAMEE
def getUsername(accountID):
    #return the repsctive username for an accounID, if the account exists
    try:
        return db.executeSQL('SELECT username FROM Accounts WHERE accountID = ?', (accountID,))[0][0]
    except IndexError:
        return('Invalid Account ID')
    

#CHECK A USERNAME IS NOT CURRENTLY IN USE
def checkGoodUsername(username):
    if len(db.executeSQL('SELECT username FROM Accounts WHERE username = ?', (username,))) == 0 and len(username) >= 8:
        return True
    else:
        return False
